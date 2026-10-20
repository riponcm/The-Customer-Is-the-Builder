SimpleScreenRecorder
====================

**Warning: The site simplescreenrecorder.com is FAKE and in no way affiliated with this project. Do NOT download SimpleScreenRecorder from that website, as it may contain malware. The only official webpage of the SimpleScreenRecorder project is [maartenbaert.be/simplescreenrecorder](https://www.maartenbaert.be/simplescreenrecorder/). See [this issue](https://github.com/MaartenBaert/ssr/issues/1086) for details.**

SimpleScreenRecorder is a screen recorder for Linux. Despite the name, this program is actually quite complex. It's 'simple' in the sense that it's easier to use than ffmpeg/avconv or VLC :).

There is a separate repository for SimpleScreenRecorder packages:
https://github.com/MaartenBaert/ssr-packages

![Screenshot](data/screenshots/screenshot01.png)

License
-------

GNU GPL v3 - read 'COPYING' for more info.

Compiling
---------

Important: If you have already installed SSR using the package manager of your distribution, you should uninstall it first before continuing!

First install the required dependencies (see below). After you have done that, you can compile and install SSR by running:

    ./simple-build-and-install

In order to use OpenGL recording for 32-bit applications on a 64-bit system, you need to compile a 32-bit version of `libssr-glinject.so`. The script will do this automatically if your system is 64-bit. Unfortunately some distributions (older versions of Debian, Ubuntu, Linux Mint, ...) don't properly support compiling 32-bit libraries on a 64-bit system, which results in errors related to missing libraries (usually libGL, libGLU) even when those libraries have in fact been installed. The problem is caused by the fact that the required symlinks are included in the `-dev` packages, but the 32-bit `-dev` packages can't be installed. The simplest solution is to skip compilation of the 32-bit GLInject library, which can be done by running:

    ENABLE_32BIT_GLINJECT=FALSE ./simple-build-and-install

You can then use SSR without the 32-bit library, or you can use the precompiled 32-bit library provided by your distribution.

If you actually want to compile the 32-bit library, you have to manually create the missing symlinks in the 32-bit library directory:

    cd /usr/lib/i386-linux-gnu
    sudo ln -s libGLU.so.1 libGLU.so
    sudo ldconfig

The OpenGL library `libGL.so` is a special case, because on some distributions (Ubuntu, Linux Mint, ...) it is installed in a different location depending on which driver you are using. If your distribution has installed the file `libGL.so.1` in the regular 32-bit library directory `/usr/lib/i386-linux-gnu` (e.g. Debian), then run this:

    cd /usr/lib/i386-linux-gnu
    sudo ln -s libGL.so.1 libGL.so
    sudo ldconfig

Otherwise you need to figure out where the library is installed first, and then manually create symlinks from the regular 32-bit library folder to this file. Note that doing this may interfere with OpenGL functionality if you ever switch to a different driver, or even just update the driver (in the case of NVIDIA). In that case you will need to manually remove the symlinks and (optionally) recreate them.

If you are using a combination of open-source and proprietary drivers (e.g. for laptops with Intel + NVIDIA GPUs a.k.a. 'Optimus'), follow only the steps for the open-source drivers.

If you are using one of the open-source drivers (i915, radeon, nouveau), then run this:

    cd /usr/lib/i386-linux-gnu
    sudo ln -s libGL.so.1 mesa/libGL.so
    sudo ln -s mesa/libGL.so libGL.so
    sudo ln -s mesa/libGL.so.1 libGL.so.1

If you are using the proprietary AMD driver, first figure out where the fglrx directory is located, this can be `/usr/lib32` or `/usr/lib/i386-linux-gnu`. Then go to the relevant folder and create the symlinks:

    cd /usr/lib/i386-linux-gnu
    sudo ln -s libGL.so.1 fglrx/libGL.so
    sudo ln -s fglrx/libGL.so libGL.so
    sudo ln -s fglrx/libGL.so.1 libGL.so.1

If you are using the proprietary NVIDIA driver, first figure out where the fglrx directory is located, this can be `/usr/lib32` or `/usr/lib/i386-linux-gnu`. Then go to the relevant folder and create the symlinks:

    cd /usr/lib/i386-linux-gnu
    sudo ln -s libGL.so.1 nvidia*/libGL.so
    sudo ln -s nvidia*/libGL.so libGL.so
    sudo ln -s nvidia*/libGL.so.1 libGL.so.1

Note that the full name of the 'nvidia' subdirectory includes the driver version number, so you will need to fix these symlinks whenever the driver has been updated.

If you want to compile step-by-step (without `simple-build-and-install`), you can use the following steps:

    mkdir build-release
    cd build-release
    cmake -DCMAKE_INSTALL_PREFIX="/usr" -DCMAKE_BUILD_TYPE=Release ..
    make
    sudo make install

Note that you may need to specify additional options depending on which Linux distribution and CPU architecture you have. The `simple-build-and-install` script detects the correct options automatically, you can run it to see which options you need.

You don't need to install the program to use it, but installing will give you a desktop entry and an icon. Also, if you don't install the program, you will need to specify where the GLInject libraries are located with `LD_LIBRARY_PATH` when using OpenGL recording.

Compilation issues
------------------

Most of these issues are avoided when using `simple-build-and-install`, but you may run into them if you run `cmake` directly.

### FFmpeg vs Libav confusion

Libav is a fork of FFmpeg that was created in 2011 as a result of a conflict between the developers. Some Linux distributions (including Debian and Ubuntu) switched to Libav because the package maintainers were among the Libav developers, while others stuck to FFmpeg. In order to deal with this situation, SSR supports both FFmpeg and Libav. In 2015 Debian and Ubuntu decided to switch back to FFmpeg for technical reasons, which means that these days very few SSR users are still using Libav. Although Libav