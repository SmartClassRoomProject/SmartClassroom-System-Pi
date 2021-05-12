# Pi-AudioModule

command to complie sharelib for python wrapper

gcc -c -fPIC Converter.c -o Converter.o
gcc -o wrap.so -shared -fPIC wrap.c

install http://audiotools.sourceforge.net/index.html
