#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <memory.h>
#include <unistd.h>  
#include <sys/mman.h>  
#include <sys/types.h>  
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>

int init_map(off_t base, size_t size, void **mapbase) {
	int res = 0;

	int fd = open("/dev/mem", O_RDWR|O_SYNC);  
	if (fd == -1)  {  
		perror("init_map open failed:");
		res = errno;
		goto cleanup;
	} 

	*mapbase = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, base);
	
	if (!*mapbase) {  
		perror("init_map mmap failed:");
		res = errno;
		goto cleanup;
	}

cleanup:
	if (fd > 0) close(fd);
	return res;
}

int loader(const char *file, unsigned long addr) {
	int res = 0;
	FILE *fp = NULL;
	char *buf = NULL;
	void *mapbase = NULL;
	size_t sz = 0, bufsz = 0, read = 0;

	if (!(fp = fopen(file, "rb"))) {
		perror("failed to open file:");
		res = errno;
		goto cleanup;
	}

	fseek(fp, 0, SEEK_END);
	sz = ftell(fp);
	fseek(fp, 0, SEEK_SET);

	// align to page size
	bufsz = (sz + 0xfff) & ~0xfff;

	fprintf(stderr, "file size: 0x%lx\n", (unsigned long)sz);
	fprintf(stderr, "alloc size: 0x%lx\n", (unsigned long)bufsz);
	fprintf(stderr, "mmap addr: 0x%lx\n", (unsigned long)addr);

	if (res = init_map(addr, bufsz, &mapbase)) {
		goto cleanup;
	}

	if (!(buf = malloc(bufsz))) {
		perror("failed to malloc:");
		res = errno;
		goto cleanup;
	}

	read = fread(buf, 0x1000, sz / 0x1000, fp) * 0x1000;
	fread(buf + read, 1, sz - read, fp);

	memcpy(mapbase, buf, bufsz);

cleanup:
	if (mapbase) munmap(mapbase, bufsz);
	if (buf) free(buf);
	if (fp) fclose(fp);
	return res;
}

int parse_addr(const char *s, unsigned long *addr) {
	unsigned long res = 0, newres;
	unsigned int radix = 10, len = strlen(s);
	unsigned char c;

	if (len > 2 && s[0] == '0' && s[1] == 'x') {
		s += 2;
		radix = 16;
	}

	while (c = *s++) {
		if (c >= '0' && c <= '9')
			c -= '0';
		else if (radix == 16) {
			if (c >= 'A' && c <= 'F')
				c -= 'A' - 10;
			else if (c >= 'a' && c <= 'f')
				c -= 'a' - 10;
			else
				return 1;
		}
		else
			return 1;

		newres = res * radix + c;
		if (newres < res)
			return 2;

		res = newres;
	}

	*addr = res;
	return 0;
}

void show_help(const char *cmd) {
	fprintf(stderr,
		"Usage:\n"
		"    %s <bin file> <address>\n",
		cmd
	);
}

int main(int argc, char *argv[]) {
	unsigned long addr;

	if (argc != 3) {
		show_help(argv[0]);
		return -1;
	}

	if (parse_addr(argv[2], &addr)) {
		fprintf(stderr, "unrecognized address: %s\n", argv[2]);
		return -1;
	}

	return loader(argv[1], addr);
} 

