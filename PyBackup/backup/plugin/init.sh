#!/usr/bin/env bash
#apt-get update
#apt-get install p7zip-full
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
export LANG=UTF-8
export LANGUAGE=UTF-8

Green_font_prefix="\033[32m" && Red_font_prefix="\033[31m" && Green_background_prefix="\033[42;37m" && Red_background_prefix="\033[41;37m" && Font_color_suffix="\033[0m"
Info="${Green_font_prefix}[信息]${Font_color_suffix}"
Error="${Red_font_prefix}[错误]${Font_color_suffix}"
Tip="${Green_font_prefix}[注意]${Font_color_suffix}"

check_sys(){
	if [[ -f /etc/redhat-release ]]; then
		release="centos"
	elif cat /etc/issue | grep -q -E -i "debian"; then
		release="debian"
	elif cat /etc/issue | grep -q -E -i "ubuntu"; then
		release="ubuntu"
	elif cat /etc/issue | grep -q -E -i "centos|red hat|redhat"; then
		release="centos"
	elif cat /proc/version | grep -q -E -i "debian"; then
		release="debian"
	elif cat /proc/version | grep -q -E -i "ubuntu"; then
		release="ubuntu"
	elif cat /proc/version | grep -q -E -i "centos|red hat|redhat"; then
		release="centos"
    fi
	bit=`uname -m`
}
Check_python(){
	python_ver=`python3 -h`
	if [[ -z ${python_ver} ]]; then
		echo -e "${Info} 没有安装Python3，开始安装..."
		if [[ ${release} == "centos" ]]; then
			yum install -y python3
			yum install python3-pip
			pip3 install --upgrade pip
			pip3 install oss2 cos-python-sdk-v5

		else
			apt-get install -y python3
			apt-get install python3-pip
			pip3 install --upgrade pip
			pip3 install oss2 cos-python-sdk-v5
		fi
	fi
	python_ver=`python3 -h`
	if [[ -z ${python_ver} ]]; then
		echo -e "${Error} 安装Python3失败，尝试编译安装..."
		wget -N --no-check-certificate https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz && tar zxvf Python-3.6.3.tgz && cd Python-3.6.3
		./configure --prefix=/opt/Python
		make && make install
		rm -rf /usr/bin/python3
		ln -s /opt/Python/bin/python3 /usr/bin/python3
		cd ..
	else
		echo -e "${Info} 安装Python3成功..."
	fi
	pip = 'pip3'
	if [[ -z ${pip} ]]; then
		echo -e "${Error} 安装Pip3失败，尝试编译安装..."
		wget https://pypi.python.org/packages/41/80/268fda78a53c2629128f8174d2952c7f902c93ebaa2062b64f27aa101b07/setuptools-38.2.3.zip#md5=0ae64455d276ff864b40aca9c06ea7c1
		unzip setuptools-38.2.3.zip
		cd setuptools-38.2.3
		python3 setup.py install
		cd ..
		wget https://pypi.python.org/packages/11/b6/abcb525026a4be042b486df43905d6893fb04f05aac21c32c638e939e447/pip-9.0.1.tar.gz#md5=35f01da33009719497f01a4ba69d63c9
		tar xf pip-9.0.1.tar.gz
		cd pip-9.0.1
		python3 setup.py install
		rm -rf /usr/bin/pip3
	    ln -s /opt/Python/bin/pip3 /usr/bin/pip3
	else
		echo -e "${Info} 安装Pip3成功..."
	fi
	pip = 'pip3'
	python_ver=`python3 -h`
	if [[ -z ${python_ver} ]]; then
		echo -e "${Error} 安装Python3失败..."
	fi
	if [[ -z ${pip} ]]; then
		echo -e "${Error} 安装Pip3失败..."
	fi
	#安装依赖
	pip3 install --upgrade pip
    pip3 install oss2 cos-python-sdk-v5
}
Centos_yum()
{
	rm -rf /var/lib/apt/lists/*
	rm -rf /var/lib/apt/lists/partial/*
	yum -y update
	yum -y install p7zip unzip
	yum -y groupinstall 'Development Tools'
	yum -y install zlib zlib-devel bzip2-devel  openssl-devel ncurses-devel
	yum -y install git
}
Debian_apt()
{
    rm -rf /var/lib/apt/lists/*
	rm -rf /var/lib/apt/lists/partial/*
	apt-get -y update
    apt-get install build-essential -y
    apt-get install libncurses5-dev libncursesw5-dev libreadline6-dev -y
    apt-get install libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev -y
    apt-get install libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev -y
    apt-get install libssl-dev openssl -y
	apt-get install -y p7zip p7zip-full unzip git
}
Download_backup_code()
{
	git clone https://github.com/LoneKingCode/PyBackup.git
}
Start()
{
	check_sys
	[[ ${release} != "debian" ]] && [[ ${release} != "ubuntu" ]] && [[ ${release} != "centos" ]] && echo -e "${Error} 本脚本不支持当前系统 ${release} !" && exit 1
	if [[ ${release} == "centos" ]]; then
		Centos_yum
	else
		Debian_apt
	fi
	Check_python
	Download_backup_code
	echo -e "${Info} 执行结束，程序在脚本执行目录..."
}

Start