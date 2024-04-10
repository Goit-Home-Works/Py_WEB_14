pwd
ls -l

#!/bin/bash

# Change directory to the current directory where the script resides
cd "$(dirname "$0")"

# Run the make command directly
docker run -v $PWD:/sphinx -w /sphinx -it sphinxdoc_builder make -C . html
cd docs
make html

#  ls -l build.sh
#  chmod +x build.sh
#  ./build.sh
