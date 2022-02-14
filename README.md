<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!---[![Contributors][contributors-shield]][contributors-url]--->
[![License][license-shield]][license-url]
<!---[![Forks][forks-shield]][forks-url]--->
<!---[![Stargazers][stars-shield]][stars-url]--->
<!---[![Issues][issues-shield]][issues-url]--->
<!---![Test Coverage][coverage-shield]--->
<!---[![LinkedIn][linkedin-shield]][linkedin-url]--->



<!-- PROJECT LOGO -->
<br />
<div align="center">
<!---
  <a href="https://gitlab.uni-hannover.de/da.schoessow/quest">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>
--->

<h3 align="center">QUEST</h3>

  <p align="center">
    QUestionnaire Editor SysTem <br /><br />
    An easy solution to create graphical user interfaces for offline questionnaires without programming knowledge.
    <br />
    <a href="https://gitlab.uni-hannover.de/da.schoessow/quest/-/wikis/overview"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <!---<a href="https://gitlab.uni-hannover.de/da.schoessow/quest">View Demo</a>
    ·--->
    <a href="https://gitlab.uni-hannover.de/da.schoessow/quest/issues">Report Bug</a>
    ·
    <a href="https://gitlab.uni-hannover.de/da.schoessow/quest/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<!--[![Product Name Screen Shot][product-screenshot]](https://example.com)-->

Questionnaires in paper form are more and more replaced with digital equivalents, but those are often hardly adaptable 
to one’s individual wishes. To simplify the use of digital questionnaires, this Python-based open-source framework was 
developed, that allows to create diverse questionnaires without any programming knowledge. The software has a graphical 
user interface as well as the possibility to edit the entire questionnaire structure in one configuration text file. 
Many common question and answer types are already implemented, but the selection will be extended. 
Furthermore, interfaces for communication with other software and systems are possible, for example OSC. 
The software is designed so that different components can also run on different computers.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

The necessary python libraries are given in ```requirements.txt```.

* [configobj](https://github.com/DiffSK/configobj) - Structure
* [fpdf](https://pyfpdf.readthedocs.io/en/latest/) - Generate pdf file
* [msgpack_python](https://pypi.org/project/msgpack/) - Communication
* [ping3](https://github.com/kyan001/ping3) - Connection check
* [PyQt5](https://pypi.org/project/PyQt5/) - GUI
* [python_osc](https://github.com/attwad/python-osc) - OSC communication
* [pyzmq](https://docs.pupil-labs.com/developer/core/network-api/#pupil-remote) - Communication
* [timeloop](https://github.com/sankalpjonn/timeloop) - Repeating jobs

### Installation

1. Clone the repo or download the [latest stable release](https://gitlab.uni-hannover.de/da.schoessow/quest/-/releases#v1.0)
   ```sh
   git clone https://gitlab.uni-hannover.de/da.schoessow/quest.git
   ```
2. Install necessary python libraries
   ```sh
   pip install requirements.txt
   ```
3. Run by executing ```Launcher.exe``` or running
   ```sh
   python launcher.py
   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
To get started, once you run the launcher, choose "Edit Questionnaire" to create our GUI.
With "Run Questionnaire" you can execute yor questionnaires.

_For more examples and explanation, please refer to the [Documentation](https://gitlab.uni-hannover.de/da.schoessow/quest/-/wikis/overview)_

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap and TODOs

- [x] Initial public release
  - [ ] Test setup
  - [ ] Initialize Wiki
- [ ] Additional question types
  - [ ] AFC
  - [ ] Localisation
- [ ] Automatic page generation/templates (e.g. pairwise comparison)
- [ ] PyQt6 compatible release
- [ ] Editor for *.qss
- [ ] Usage of Mad Mapper as video tool (OSC support given)
- [ ] Fix pdf export graphic glitches
- [ ] svgs for CheckBox and RadioButton
- [ ] automatic centering of SliderHeader/MatrixHeader
- [ ] images/videos as element for the questionnaire
- [ ] support for multiple languages
- [ ] "if this answer than go to that page"-logic

See the [open issues](https://gitlab.uni-hannover.de/da.schoessow/quest/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the GNU GPLv3 License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Daphne Schössow - [daphne.schoessow@ikt.uni-hannover.de](mailto:daphne.schoessow@ikt.uni-hannover.de)

Project Link: [https://gitlab.uni-hannover.de/da.schoessow/quest](https://gitlab.uni-hannover.de/da.schoessow/quest)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
<!---## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#top">back to top</a>)</p>

--->

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
<!--- [contributors-shield]: https://img.shields.io/github/contributors/da.schoessow/quest.svg?style=for-the-badge
[contributors-url]: https://gitlab.uni-hannover.de/da.schoessow/quest/graphs/contributors --->
[forks-shield]: https://img.shields.io/badge/dynamic/json?color=white&label=Forks&query=$.forks_count&url=https://gitlab.uni-hannover.de/api/v4/projects/1829
<!---https://img.shields.io/github/forks/da.schoessow/quest.svg?style=for-the-badge--->
[forks-url]: https://gitlab.uni-hannover.de/da.schoessow/quest/-/forks
[stars-shield]: https://img.shields.io/badge/dynamic/json?color=white&label=Stars&query=$.star_count&url=https://gitlab.uni-hannover.de/api/v4/projects/1829
<!---https://img.shields.io/github/stars/da.schoessow/quest.svg?style=for-the-badge--->
[stars-url]: https://gitlab.uni-hannover.de/da.schoessow/quest/-/starrers
[issues-shield]:  https://img.shields.io/badge/dynamic/json?color=white&label=Issues&query=$.open_issues_count&url=https://gitlab.uni-hannover.de/api/v4/projects/1829
<!---https://img.shields.io/github/issues/da.schoessow/quest.svg?style=for-the-badge--->
[issues-url]: https://gitlab.uni-hannover.de/da.schoessow/quest/-/issues
[license-shield]: https://img.shields.io/badge/License-GNU%20GPLv3-white
<!---https://img.shields.io/github/license/da.schoessow/quest.svg?style=for-the-badge--->
[license-url]: https://gitlab.uni-hannover.de/da.schoessow/quest/-/blob/main/LICENSE
<!---[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username --->
[product-screenshot]: images/screenshot.png
[coverage-shield]: https://gitlab.uni-hannover.de/da.schoessow/quest/badges/main/coverage.svg
<!---https://img.shields.io/github/coverage/da.schoessow/quest/main.svg?style=for-the-badge--->
