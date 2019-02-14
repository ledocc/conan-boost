project(MyHello)
cmake_minimum_required(VERSION 2.8)
enable_testing()

set(Boost_DEBUG 1)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")
if(CONAN_SETTINGS_OS STREQUAL "Android")
    set(CONAN_LIBCXX "") # NDK fails when specified: https://github.com/android-ndk/ndk/issues/541
endif()

conan_basic_setup()

if(NOT HEADER_ONLY)
    list(FIND CONAN_DEFINES_BOOST "-DBOOST_USE_STATIC_LIBS" IS_STATIC)
    file(READ ${CMAKE_BINARY_DIR}/conaninfo.txt CONANINFO)
    string(FIND ${CONANINFO} "boost:skip_lib_rename=True" IS_SKIP_LIB_RENAME)
    if(${IS_STATIC} GREATER -1 AND ${IS_SKIP_LIB_RENAME} GREATER -1)
        set(Boost_USE_STATIC_LIBS ON)
    endif()
    if(WITH_PYTHON)
        find_package(Boost COMPONENTS regex python locale REQUIRED)
    else()
        find_package(Boost COMPONENTS regex locale REQUIRED)
    endif()

    include_directories(${Boost_INCLUDE_DIRS})
    add_executable(lambda lambda.cpp)
    add_executable(regex_exe regex.cpp)
    add_executable(test test.cpp)
    target_link_libraries(regex_exe ${Boost_LIBRARIES})
    message("LIBS=> ${CONAN_LIBS}")
    target_link_libraries(test ${CONAN_LIBS})
    if(WITH_PYTHON)
        add_library(hello_ext SHARED python.cpp)
        if(WIN32)
            set_target_properties(hello_ext PROPERTIES SUFFIX ".pyd")
            target_include_directories(hello_ext PRIVATE C:/Python27/include)
            target_link_libraries(hello_ext C:/Python27/libs/python27.lib ${CONAN_LIBS})
        endif()
    endif()
    add_test(NAME TestRegex
             COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:regex_exe>")


    if(USE_ICU)
        add_executable(use_icu use_icu.cpp)
        target_link_libraries(use_icu ${Boost_LIBRARIES} )

        list( FIND CONAN_DEFINES_ICU "-DU_STATIC_IMPLEMENTATION" ICU_STATIC_DEFINE_INDEX )
        if( ${ICU_STATIC_DEFINE_INDEX} GREATER -1 )

            find_package(Boost COMPONENTS thread REQUIRED)
            target_link_libraries(use_icu ${Boost_LIBRARIES} )

            find_package(ICU COMPONENTS tu i18n io uc data REQUIRED)
            target_link_libraries(use_icu ${ICU_LIBRARIES} )

            if(UNIX)
                find_package( Iconv REQUIRED )
                if( Iconv_FOUND AND NOT Iconv_IS_BUILT_IN )
                    target_link_libraries( use_icu ${Iconv_LIBRARIES} )
                endif()
                if( NOT APPLE )
                    target_link_libraries( use_icu dl )
                endif()
            endif()

        endif()

        add_test(NAME TestUseICU
            COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:use_icu>")
    endif()

else()
    add_executable(lambda lambda.cpp)
endif()

add_test(NAME TestLambda
         COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:lambda>" ${TEST_ARGS})

if(NOT HEADER_ONLY)
    # Test a different exe linking with the CONAN_LIBS to actually test the package_info
    add_executable(newregex regex.cpp)
    target_link_libraries(newregex ${CONAN_LIBS})
    add_test(NAME TestRegexNew
             COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:newregex>" ${TEST_ARGS})
endif()
