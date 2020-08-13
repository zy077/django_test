#!/bin/bash
mysql -h数据库ip地址 -u数据库用户名 -p 数据库密码 < areas.sql
mysql -h localhost -u root -p mysql < areas.sql
