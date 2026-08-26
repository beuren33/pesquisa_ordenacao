ASM = nasm -f elf64
CC = gcc

all: libsort.so

bubble_sort.o: asm/bubble_sort.asm
	$(ASM) -o bubble_sort.o asm/bubble_sort.asm

insertion_sort.o: asm/insertion_sort.asm
	$(ASM) -o insertion_sort.o asm/insertion_sort.asm

shell_sort.o: asm/shell_sort.asm
	$(ASM) -o shell_sort.o asm/shell_sort.asm

selection_sort.o: asm/selection_sort.asm
	$(ASM) -o selection_sort.o asm/selection_sort.asm

quick_sort.o: asm/quick_sort.asm
	$(ASM) -o quick_sort.o asm/quick_sort.asm

merge_sort.o: asm/merge_sort.asm
	$(ASM) -o merge_sort.o asm/merge_sort.asm

libsort.so: bubble_sort.o insertion_sort.o shell_sort.o selection_sort.o quick_sort.o merge_sort.o
	$(CC) -shared -o libsort.so bubble_sort.o insertion_sort.o shell_sort.o selection_sort.o quick_sort.o merge_sort.o

clean:
	rm -f *.o libsort.so

.PHONY: all clean
