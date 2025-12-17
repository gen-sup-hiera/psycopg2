psycopg2 Python Library for AWS Lambda
======================================

### How to use

#### Python 3
Just copy the psycopg2-3.9 or psycopg2-3.12 directory into AWS Lambda repository and rename it to psycopg2 before creating your AWS Lambda zip package.

### Instructions on compiling this package from scratch for Python 3.10 and higher

1. Download the
  [PostgreSQL source code](https://ftp.postgresql.org/pub/source/v9.4.3/postgresql-9.4.3.tar.gz) and extract into a directory.
  - `wget https://ftp.postgresql.org/pub/source/v9.4.3/postgresql-9.4.3.tar.gz`
  - `tar -xvzf postgresql-9.4.3.tar.gz`
2. Download the
  - [psycopg2 source code](https://files.pythonhosted.org/packages/fc/07/e720e53bfab016ebcc34241695ccc06a9e3d91ba19b40ca81317afbdc440/psycopg2-binary-2.9.9.tar.gz) and extract into a directory.
  - `wget https://files.pythonhosted.org/packages/fc/07/e720e53bfab016ebcc34241695ccc06a9e3d91ba19b40ca81317afbdc440/psycopg2-binary-2.9.9.tar.gz`
  - `tar -xvzf psycopg2-binary-2.9.9.tar.gz`
3. Go into the PostgreSQL source directory and execute the following commands:
  - `./configure --prefix {path_to_postgresql_source} --without-readline --without-zlib`
  - `make`
  - `make install`
4. Go into the psycopg2 source directory and edit the `setup.cfg` file with the following:
  - `pg_config={path_to_postgresql_source/bin/pg_config}`
  - `static_libpq=1`
5. Execute `pip3.10 install psycopg2-binary`. (Use approriate pip  version for Python > 3.10)
6. Install PostgreSQL development files:
 - On Ubuntu or other Debian-based OS - `sudo apt-get install libpq-dev python-dev`
 - On Fedora, RHEL, CentOS or similar - `sudo yum install postgresql-devel python-devel`
7. Execute `python3.10 setup.py build` in the psycopg2 source directory. (Use corresponding python version for Python > 3.10)
8. After the above steps have been completed you will then have a build directory like `/psycopg2-2.9.9/build/lib.linux-x86_64-cpython-310/`
and the custom compiled `psycopg2` library will be contained within it.
9. Create a new folder `lambda_function_310` and copy build files to it.

### Instructions how to use complied library

If there is a nessecity to use Python 3.10 and higher in a Lambda function, copy psycopg2 library built in steps above by putting library source code under the directory `lambda_function\psycopg2`

Original guide can be found at `https://github.com/jkehler/awslambda-psycopg2/tree/master`
