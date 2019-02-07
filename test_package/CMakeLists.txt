PROJECT(MyHello)
cmake_minimum_required(VERSION 2.8)
enable_testing()

set(Boost_DEBUG 1)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")
if(CONAN_SETTINGS_OS STREQUAL "Android")
    set(CONAN_LIBCXX "") # NDK fails when specified: https://github.com/android-ndk/ndk/issues/541
endif()

CONAN_BASIC_SETUP()

IF(NOT HEADER_ONLY)
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
    ADD_EXECUTABLE(lambda lambda.cpp)
    ADD_EXECUTABLE(regex_exe regex.cpp)
    ADD_EXECUTABLE(test test.cpp)
    TARGET_LINK_LIBRARIES(regex_exe ${Boost_LIBRARIES})
    MESSAGE("LIBS=> ${CONAN_LIBS}")
    TARGET_LINK_LIBRARIES(test ${CONAN_LIBS})
    if(WITH_PYTHON)
        add_library(hello_ext SHARED python.cpp)
        if(WIN32)
            set_target_properties(hello_ext PROPERTIES SUFFIX ".pyd")
            target_include_directories(hello_ext PRIVATE C:/Python27/include)
            target_link_libraries(hello_ext C:/Python27/libs/python27.lib ${CONAN_LIBS})
        endif()
    endif()
    ADD_TEST(NAME TestRegex
             COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:regex_exe>")


    if(USE_ICU)
        ADD_EXECUTABLE(use_icu use_icu.cpp)
        TARGET_LINK_LIBRARIES(use_icu ${Boost_LIBRARIES} )


        list( FIND CONAN_DEFINES_ICU "-DU_STATIC_IMPLEMENTATION" ICU_STATIC_DEFINE_INDEX )
        if( ${ICU_STATIC_DEFINE_INDEX} GREATER -1 )

            find_package(Boost COMPONENTS thread REQUIRED)
            TARGET_LINK_LIBRARIES(use_icu ${Boost_LIBRARIES} )

            find_package(ICU COMPONENTS tu i18n io uc data REQUIRED)
            TARGET_LINK_LIBRARIES(use_icu ${ICU_LIBRARIES} )

            if(UNIX)
                find_package( Iconv REQUIRED )
                if( Iconv_FOUND AND NOT Iconv_IS_BUILT_IN )
                    TARGET_LINK_LIBRARIES( use_icu ${Iconv_LIBRARIES} )
                endif()
                if( NOT APPLE )
                    TARGET_LINK_LIBRARIES( use_icu dl )
                endif()
            endif()

        endif()

        ADD_TEST(NAME TestUseICU
            COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:use_icu>")
    endif()

ELSE()
    ADD_EXECUTABLE(lambda lambda.cpp)
ENDIF()

ADD_TEST(NAME TestLambda
         COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:lambda>" ${TEST_ARGS})

IF(NOT HEADER_ONLY)
    # Test a different exe linking with the CONAN_LIBS to actually test the package_info
    ADD_EXECUTABLE(newregex regex.cpp)
    TARGET_LINK_LIBRARIES(newregex ${CONAN_LIBS})
    ADD_TEST(NAME TestRegexNew
             COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:newregex>" ${TEST_ARGS})
ENDIF()
