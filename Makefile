ASM = nasm -f elf64
CC = gcc

all: libsort.so

bubble_sort.o: asm/bubble_sort.asm
	$(ASM) -o bubble_sort.o asm/bubble_sort.asm

insertion_sort.o: asm/insertion_sort.asm
	$(ASM) -o insertion_sort.o asm/insertion_sort.asm

libsort.so: bubble_sort.o insertion_sort.o
	$(CC) -shared -o libsort.so bubble_sort.o insertion_sort.o

clean:
	rm -f *.o libsort.so

.PHONY: all clean
