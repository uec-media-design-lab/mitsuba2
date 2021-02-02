<img src="https://github.com/mitsuba-renderer/mitsuba2/raw/master/docs/images/logo_plain.png" width="120" height="120" alt="Mitsuba logo">

# Mitsuba Renderer 2
<!--
| Documentation   | Linux             | Windows             |
|      :---:      |       :---:       |        :---:        |
| [![docs][1]][2] | [![rgl-ci][3]][4] | [![appveyor][5]][6] |


[1]: https://readthedocs.org/projects/mitsuba2/badge/?version=master
[2]: https://mitsuba2.readthedocs.io/en/latest/src/getting_started/intro.html
[3]: https://rgl-ci.epfl.ch/app/rest/builds/buildType(id:Mitsuba2_Build)/statusIcon.svg
[4]: https://rgl-ci.epfl.ch/viewType.html?buildTypeId=Mitsuba2_Build&guest=1
[5]: https://ci.appveyor.com/api/projects/status/eb84mmtvnt8ko8bh/branch/master?svg=true
[6]: https://ci.appveyor.com/project/wjakob/mitsuba2/branch/master
-->
| Documentation   |
|      :---:      |
| [![docs][1]][2] |


[1]: https://readthedocs.org/projects/mitsuba2/badge/?version=latest
[2]: https://mitsuba2.readthedocs.io/en/latest/src/getting_started/intro.html

Mitsuba 2 is a research-oriented rendering system written in portable C++17. It
consists of a small set of core libraries and a wide variety of plugins that
implement functionality ranging from materials and light sources to complete
rendering algorithms. Mitsuba 2 strives to retain scene compatibility with its
predecessor [Mitsuba 0.6](https://github.com/mitsuba-renderer/mitsuba).
However, in most other respects, it is a completely new system following a
different set of goals.

The most significant change of Mitsuba 2 is that it is a *retargetable*
renderer: this means that the underlying implementations and data structures
are specified in a generic fashion that can be transformed to accomplish a
number of different tasks. For example:

1. In the simplest case, Mitsuba 2 is an ordinary CPU-based RGB renderer that
   processes one ray at a time similar to its predecessor [Mitsuba
   0.6](https://github.com/mitsuba-renderer/mitsuba).

2. Alternatively, Mitsuba 2 can be transformed into a differentiable renderer
   that runs on NVIDIA RTX GPUs. A differentiable rendering algorithm is able
   to compute derivatives of the entire simulation with respect to input
   parameters such as camera pose, geometry, BSDFs, textures, and volumes. In
   conjunction with gradient-based optimization, this opens door to challenging
   inverse problems including computational material design and scene reconstruction.

3. Another type of transformation turns Mitsuba 2 into a vectorized CPU
   renderer that leverages Single Instruction/Multiple Data (SIMD) instruction
   sets such as AVX512 on modern CPUs to efficiently sample many light paths in
   parallel.

4. Yet another type of transformation rewrites physical aspects of the
   simulation: Mitsuba can be used as a monochromatic renderer, RGB-based
   renderer, or spectral renderer. Each variant can optionally account for the
   effects of polarization if desired.

In addition to the above transformations, there are
several other noteworthy changes:

1. Mitsuba 2 provides very fine-grained Python bindings to essentially every
   function using [pybind11](https://github.com/pybind/pybind11). This makes it
   possible to import the renderer into a Jupyter notebook and develop new
   algorithms interactively while visualizing their behavior using plots.

2. The renderer includes a large automated test suite written in Python, and
   its development relies on several continuous integration servers that
   compile and test new commits on different operating systems using various
   compilation settings (e.g. debug/release builds, single/double precision,
   etc). Manually checking that external contributions don't break existing
   functionality had become a severe bottleneck in the previous Mitsuba 0.6
   codebase, hence the goal of this infrastructure is to avoid such manual
   checks and streamline interactions with the community (Pull Requests, etc.)
   in the future.

3. An all-new cross-platform user interface is currently being developed using
   the [NanoGUI](https://github.com/mitsuba-renderer/nanogui) library. *Note
   that this is not yet complete.*

## Compiling and using Mitsuba 2

Please see the [documentation](http://mitsuba2.readthedocs.org/en/latest) for
details on how to compile, use, and extend Mitsuba 2.

## Clone

```
git clone --recursive https://github.com/uec-media-design-lab/mitsuba2.git
cd mitsuba2
git submodule update --init --recursive
```

## Choosing variants
variantsを変更したり、追加してmitsuba2のアプリケーション（偏光レンダリング、微分可能レンダリング）を利用できる。
[Variants list](https://mitsuba2.readthedocs.io/en/latest/src/getting_started/variants.html)

### How to add and/or modify variants
```
cd <..mitsuba repository..>
cp resources/mitsuba.conf.template mitsuba.conf
```
`mitsuba.conf` を開いて、好みのvariants(`gpu_rgb`, `gpu_autodiff_rgb`, etc...)を追記する。
```json
"enabled": [
    # The "scalar_rgb" variant *must* be included at the moment.
    "scalar_rgb",
    "scalar_spectral",
    "gpu_rgb",          # Add
    "gpu_autodiff_rgb"  # Add
],
```

## Compile
### Linux
Clangや必要なモジュールを以下のコマンドでインストールする。
```
# Install recent versions build tools, including Clang and libc++ (Clang's C++ library)
sudo apt install -y clang-9 libc++-9-dev libc++abi-9-dev cmake ninja-build

# Install libraries for image I/O and the graphical user interface
sudo apt install -y libz-dev libpng-dev libjpeg-dev libxrandr-dev libxinerama-dev libxcursor-dev

# Install required Python packages
sudo apt install -y python3-dev python3-distutils python3-setuptools
```

テストやHTMLドキュメントを生成するためには追加のパッケージが必要(see [Developer guide](https://mitsuba2.readthedocs.io/en/latest/src/developer_guide/intro.html#sec-devguide))。以下のコマンドでインストール。

```
# For running tests
sudo apt install -y python3-pytest python3-pytest-xdist python3-numpy

# For generating the documentation
sudo apt install -y python3-sphinx python3-guzzle-sphinx-theme python3-sphinxcontrib.bibtex
```

Next, ensure that two environment variables CC and CXX are exported. You can either run these two commands manually before using CMake or—even better—add them to your ~/.bashrc file. This ensures that CMake will always use the correct compiler.
CC、CXXの環境変数を変更する。~/.bashrcに以下のコマンドを追記することで、terminal起動時に必ず環境変数設定が実行される。zshなどのbashではないシェルを使っている場合はシェルに合わせて変更する(.zshrcなど)。

```
export CC=clang-9
export CXX=clang++-9
```
コンパイルは以下コマンド。

```
# Create a directory where build products are stored
cd <..mitsuba repository..>
mkdir build
cd build
cmake -GNinja ..
ninja
```

### Windows
- 必要環境
   - Visual Studio 2019.
   - git 
   - CMake
   - Python (Anacondaの利用を進めます。少なくとも木内の環境では、Anacondaを使わないとコンパイル後にPythonから `import mitsuba` としても、Pythonがmitsubaを認識してくれませんでした。Anaconda promptで実行したところ、うまく動作することを確認しています。

```
# To be safe, explicitly ask for the 64 bit version of Visual Studio
mkdir build
cd build
cmake .. -G "Visual Studio 16 2019" -A x64
```

Afterwards, open the generated mitsuba.sln file and proceed building as usual from within Visual Studio. You will probably also want to set the build mode to Release there.
buildディレクトリ下に`mitsuba.sln`が生成されるので、Visual Studioで開く。Releaseビルドを選択して、タブから`ソリューションのビルド`を実行。

または、[`msbuild`](https://docs.microsoft.com/en-us/cpp/build/walkthrough-using-msbuild-to-create-a-visual-cpp-project?redirectedfrom=MSDN&view=msvc-160) を利用する。

[VC 2017のIDE上から64bitのcl.exeを使う](https://ameblo.jp/michirushiina/entry-12277257163.html)に記載のように、コンパイルに使用するメモリが2GBを超えると、「ヒープの領域を使い果たしました。」みたいなエラーが出ることがある。
原因はIDEが32bitアプリで、コンパイルも32bit版が走るかららしい。
`msbuild`を利用すると、64bitコンパイルで指定ができるので、上記エラーがでない&コマンドラインから実行ができるので便利。

:warning: MSBuild.exeへの環境変数は通す必要あり。
```
C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\<バージョン(16.0など)>\Bin\MSBuild.exe
```

```
msbuild mitsuba.sln /p:configuration=release /p:platform=x64 /p:PreferredToolArchitecture=x64
```


## About

This project was created by [Wenzel Jakob](http://rgl.epfl.ch/people/wjakob).
Significant features and/or improvements to the code were contributed by
[Merlin Nimier-David](https://merlin.nimierdavid.fr/),
[Guillaume Loubet](https://maverick.inria.fr/Membres/Guillaume.Loubet/),
[Benoît Ruiz](https://github.com/4str0m),
[Sébastien Speierer](https://github.com/Speierers),
[Delio Vicini](https://dvicini.github.io/),
and [Tizian Zeltner](https://tizianzeltner.com/).
