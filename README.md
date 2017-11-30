## Restaurant Menu App Project
by Mostafa Elsheikh, in fulfillment of Udacity's <i class="icon-cog"></i> **[Full Stack Web Developer Nanodegree](https://www.udacity.com/course/nd004)**

### About

Restaurant Menu App is a web application developed using `Flask`, a Python framework.
This application deals with a `SQLite` database which has Restaurants, and Menu Items. It is styled using `Bootstrap` and `Font-Awesome`.

This application shows list of restaurants, and their menu items. It has the ability to create, edit, or remove any of them as well.

#### Prerequisites
* Python 3
* [VirtualBox](virtualbox.org)
* [Vagrant](https://www.vagrantup.com/downloads.html)
* PowerShell or Bash

#### Install Vagrant
Download: https://www.vagrantup.com/downloads.html

**Windows users:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

If Vagrant is successfully installed, you will be able to run `vagrant --version`
in your terminal to see the version number.

#### Download VM configuration

You can download and unzip file https://github.com/Sasa94s/FullStack-ND/archive/master.zip, will be located in folder `Project 3`. or you can clone repository using git command `git clone https://github.com/Sasa94s/FullStack-ND.git`

### How To Run

If you need to bring the virtual machine back online (with `vagrant up`), do so now. Then log into it with `vagrant ssh`.

Change your directory to `cd /vagrant/Restaurant-Menu-App/`

To execute the program, run `python finalProject.py` using the command line.