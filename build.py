from conan.packager import ConanMultiPackager
import copy
import os
import platform


def _add_locale_use_icu_if_build_shared_library(filtered_builds, settings, options, env_vars, build_requires):
    if options["boost:shared"] is True:
        options_local_use_icu = options.copy()
        options_local_use_icu["boost:locale_use_icu"] = True
        filtered_builds.append([settings, options_local_use_icu, env_vars, build_requires])





if __name__ == "__main__":
    builder = ConanMultiPackager()

    if os.getenv("HEADER_ONLY"):

        builder.add({}, {"boost:header_only": True})
    else:
        builder.add_common_builds(shared_option_name="boost:shared", pure_c=False)

        if platform.system() == "Windows":
            filtered_builds = []
            for settings, options, env_vars, build_requires in builder.builds:
                _add_locale_use_icu_if_build_shared_library(filtered_builds,
                                                            settings, options, env_vars, build_requires)
                # MinGW shared with linker errors. I don't have a clue
                if settings["compiler"] == "gcc" and options["boost:shared"] is True:
                    continue
                filtered_builds.append([settings, options, env_vars, build_requires])
            builder.builds = filtered_builds
        if platform.system() == "Linux":
            filtered_builds = []
            for settings, options, env_vars, build_requires in builder.builds:
                _add_locale_use_icu_if_build_shared_library(filtered_builds,
                                                            settings, options, env_vars, build_requires)
                if settings["compiler"] == "clang":
                    settings_libstdcxx11 = settings.copy()
                    settings_libstdcxx11["compiler.libcxx"] = "libstdc++11"
                    filtered_builds.append([settings_libstdcxx11, options, env_vars, build_requires])
                filtered_builds.append([settings, options, env_vars, build_requires])
            builder.builds = filtered_builds
    builder.run()
