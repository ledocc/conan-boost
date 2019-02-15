cmake_minimum_required(VERSION 2.8)





##--------------------------------------------------------------------------------------------------------------------##
## define usefull function
##--------------------------------------------------------------------------------------------------------------------##
#
# target_use_boost( target components [components ...])
#  add boost's component information ( includes, libs, defines, ...) to target's property
#
function(target_use_boost target )

#    set(Boost_DEBUG 1)
    find_package( Boost COMPONENTS ${ARGN} REQUIRED )
    target_include_directories( ${target} PUBLIC ${boost_INCLUDE_DIRS} )
    target_link_libraries(      ${target} PUBLIC ${Boost_LIBRARIES} )

endfunction()

macro(find_python python_version)

    if( ${python_version} MATCHES "^2(\\.[0-9]+)*$" )
        set(python_major_version 2)
    elseif( ${python_version} MATCHES "^3(\\.[0-9]+)*$" )
        set(python_major_version 3)
    else()
        message(FATAL_ERROR "Invalid python version : ${python_version}")
    endif()

    set(Python_ADDITIONAL_VERSIONS ${python_version})
    find_package(PythonInterp)
    find_package(PythonLibs)

endmacro()

function(target_use_python target python_version)

    message(STATUS "PYTHON_INCLUDE_DIRS = ${PYTHON_INCLUDE_DIRS}")
    message(STATUS "PYTHON_LIBRARIES = ${PYTHON_LIBRARIES}")

    target_include_directories( ${target} PUBLIC ${PYTHON_INCLUDE_DIRS} )
    target_link_libraries(      ${target} PUBLIC ${PYTHON_LIBRARIES} )

endfunction()



##--------------------------------------------------------------------------------------------------------------------##
## define project
##--------------------------------------------------------------------------------------------------------------------##
project(ConanBoostTestPackage)
enable_testing()

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")



##--------------------------------------------------------------------------------------------------------------------##
## define conan's information
##--------------------------------------------------------------------------------------------------------------------##
include( "${CMAKE_BINARY_DIR}/conanbuildinfo.cmake" )
if(CONAN_SETTINGS_OS STREQUAL "Android")
    set(CONAN_LIBCXX "") # NDK fails when specified: https://github.com/android-ndk/ndk/issues/541
endif()
conan_basic_setup()



##--------------------------------------------------------------------------------------------------------------------##
## add test for boost's include ( use lambda headers )
##--------------------------------------------------------------------------------------------------------------------##
add_executable( lambda_exe lambda.cpp )
target_use_boost( lambda_exe )
add_test( NAME TestLambda
          COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:lambda_exe>" ${TEST_ARGS} )


if(HEADER_ONLY)
    return()
endif()


##--------------------------------------------------------------------------------------------------------------------##
## detect if boost is statically linked
##--------------------------------------------------------------------------------------------------------------------##
list(FIND CONAN_DEFINES_BOOST "-DBOOST_USE_STATIC_LIBS" IS_STATIC)


##--------------------------------------------------------------------------------------------------------------------##
## detect if boost is renamed
##--------------------------------------------------------------------------------------------------------------------##
file(READ ${CMAKE_BINARY_DIR}/conaninfo.txt CONANINFO)
string(FIND ${CONANINFO} "boost:skip_lib_rename=True" IS_SKIP_LIB_RENAME)





if(${IS_STATIC} GREATER -1 AND ${IS_SKIP_LIB_RENAME} GREATER -1)
    set(Boost_USE_STATIC_LIBS ON)
endif()


##--------------------------------------------------------------------------------------------------------------------##
## add test for boost's libraries ( use regex library )
##--------------------------------------------------------------------------------------------------------------------##
add_executable( regex_exe regex.cpp )
target_use_boost( regex_exe regex )
add_test(NAME TestRegex
    COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:regex_exe>")



##--------------------------------------------------------------------------------------------------------------------##
## add test for boost's python
##--------------------------------------------------------------------------------------------------------------------##
if(WITH_PYTHON)
    find_python( ${PYTHON_VERSION} )
    python_add_module( boost_python_hello boost_python_hello.cpp )
    set_target_properties( boost_python_hello PROPERTIES LIBRARY_OUTPUT_DIRECTORY bin)
    set_target_properties( boost_python_hello PROPERTIES LIBRARY_OUTPUT_DIRECTORY_RELEASE bin)
    set_target_properties( boost_python_hello PROPERTIES LIBRARY_OUTPUT_DIRECTORY_DEBUG bin)

    string(REPLACE "." "" PYTHON_VERSION_NOT_DOT ${PYTHON_VERSION})
    target_use_boost( boost_python_hello python${PYTHON_VERSION_NOT_DOT} )
    target_use_python( boost_python_hello ${PYTHON_VERSION} )

    file(COPY boost_python_hello.py DESTINATION bin)
    add_test(NAME TestPython
        COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} ${PYTHON_EXECUTABLE} "bin/boost_python_hello.py")
endif()


##--------------------------------------------------------------------------------------------------------------------##
## add test for boost:use_icu option
##--------------------------------------------------------------------------------------------------------------------##
if(USE_ICU)
    add_executable( use_icu_exe use_icu.cpp )
    target_use_boost( use_icu_exe locale )

    list( FIND CONAN_DEFINES_ICU "-DU_STATIC_IMPLEMENTATION" ICU_STATIC_DEFINE_INDEX )
    if( ${ICU_STATIC_DEFINE_INDEX} GREATER -1 )

        target_use_boost( use_icu_exe thread )

        find_package(ICU COMPONENTS tu i18n io uc data REQUIRED)
        target_link_libraries(use_icu_exe ${ICU_LIBRARIES} )

        if(UNIX)
            find_package( Iconv REQUIRED )
            if( Iconv_FOUND AND NOT Iconv_IS_BUILT_IN )
                target_link_libraries( use_icu_exe ${Iconv_LIBRARIES} )
            endif()
            if( NOT APPLE )
                target_link_libraries( use_icu_exe dl )
            endif()
        endif()

    endif()

    add_test(NAME TestUseICU
        COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:use_icu_exe>")
endif()




##--------------------------------------------------------------------------------------------------------------------##
## test a different exe linking with the CONAN_LIBS to actually test the package_info
##--------------------------------------------------------------------------------------------------------------------##

add_executable( test_exe_linked_with_conan_info test.cpp )
target_link_libraries( test_exe_linked_with_conan_info ${CONAN_LIBS} )

add_executable( regex_exe_linked_with_conan_info regex.cpp )
target_link_libraries( regex_exe_linked_with_conan_info ${CONAN_LIBS} )
add_test(
    NAME TestRegexLinkedWithConanInfo
    COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:regex_exe_linked_with_conan_info>" ${TEST_ARGS}
)
