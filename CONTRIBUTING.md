# Contributing to the Privacy Protocol

First off, thank you for considering contributing to the Privacy Protocol. It's people like you that make the open source community such a great place.

## Guiding Principles

This project is guided by a few core principles:

*   **Expanded KISS (Keep It Simple, Stupid):** We strive for simplicity in our code and our documentation.
*   **Law of Constant Progression:** We are always moving forward, iterating and improving.
*   **Battle-Tested Mentality:** We believe in rigorous testing and building robust, reliable software.

## Prerequisites

Before you get started, you will need to have the following tools installed:

*   Python 3.9+
*   pip
*   virtualenv

## Getting Started

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/BigBossBooling/PrivacyProtocol.git
    cd PrivacyProtocol
    ```

2.  **Create a virtual environment:**

    ```bash
    virtualenv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements-dev.txt
    ```

## Contribution Workflow

1.  **Create a new branch:**

    ```bash
    git checkout -b feature/my-new-feature
    ```

2.  **Make your changes.**

3.  **Run the tests:**

    ```bash
    python -m unittest discover tests
    ```

4.  **Commit your changes:**

    ```bash
    git commit -am 'feat: Add some feature'
    ```

5.  **Push to the branch:**

    ```bash
    git push origin feature/my-new-feature
    ```

6.  **Create a new Pull Request.**

## Pull Request Process

1.  Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2.  Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3.  Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
4.  You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## Code of Conduct

This project and everyone participating in it is governed by the [QRASL Code of Conduct](https://github.com/BigBossBooling/QRASL/blob/main/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [josephis.wade@gmail.com](mailto:josephis.wade@gmail.com).

## Reporting Issues

If you find a bug or have a feature request, please [open an issue](https://github.com/BigBossBooling/PrivacyProtocol/issues).
