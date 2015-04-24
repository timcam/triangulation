#include <stdio.h>

/* Read .node files into a list */

main(int argc, char *argv[]){

	FILE *fp;
	void filecopy(FILE *, FILE *);
	//char *prog = argv[0];

	if (argc == 1) 
		filecopy(stdin, stdout);
	else
		while (--argc > 0)
			if ((fp = fopen(*++argv, "r")) == NULL) {
				printf("cat: cannot open %s\n", *argv);
				return 1;
			} else {
				filecopy(fp, stdout);
				fclose(fp);
			}
	return 0;
}

/* filecopy copy inputfile to output file */
void filecopy(FILE *ifp, FILE *ofp)
{ 
 	/* reads the first line of the file  */
	int numVert, dimensions;
	numVert = 0;
	fscanf(ifp, "%i %i", &numVert, &dimensions);

	printf("%i %i\n", numVert, dimensions);

	float vertices[numVert];
}

// char *fgets(char *s, int n, FILE *iop){
// 	register int c;
// 	register char *cs;

// 	cs = s;
// 	while (--n > 0 && (c = getc(iop)) != EOF)
// 		if ((*cs++ = c) == '\n')
// 			break;
// 	*cs  = '\0';
// 	return (c == EOF && cs == s) ? NULL : s;
// }

void getline(char *line, int max){
	if (fgets(line))

}
