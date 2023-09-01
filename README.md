# ByeBob
A python package for automating time submitting via `hibob` app and `jumpcloud` authorization.

## Installation

1. Clone the repository and enter it:

    ```sh
    $ git clone git@github.com:sahargavriely/byebob.git
    ...
    $ cd byebob/
    ```

2. Run the installation script and activate the virtual environment according to your operating system:

    ```sh
    $ ./scripts/install.sh
    ...
    $ source .env/bin/activate
    [byebob] $  # you're good to go!
    ```

3. Create a directory by the name of ``webdrivers``. Download chrome web driver and save it in this directory under the name of ``chromedriver.exe``:

    ```sh
    $ mkdir webdrivers
    ...
    $ ls webdrivers/
    chromedriver.exe
    ```

## Configuration

Before we dive in there are some configuration you need to set in advance.
The configuration are located under ``byebob/__main__.py``
```
email = ''
password = ''
start_hour_range = 8, 10  # The range of hours which the day start submitting time will randomized from
hours_a_day_range = 9, 12  # The range of hours which the day will take will randomized from
```

## Usage

Execute the python package and follow the instruction

```sh
$ python -m byebob
```
