# crontab
➜ crontab ✗ tree
.
├── README.md(使用说明文件)
├── bin(可执行脚本/二进制可执行文件存放目录)
│   ├── kglobal.py(通用函数模块)
│   ├── crontab.py(crontab模块)
│   └── service.py(调度模块)
├── etc(配置文件存放目录)
│   ├── crontab.cfg(crontab配置文件)
│   ├── service.cfg(service配置文件)
│   └── global.cfg(全局配置文件)
├── lock(锁文件存放目录)
│   └── crontab.lock(crontab锁文件)
└── log(日志文件存放目录)
    └── crontab.log(crontab日志文件)
