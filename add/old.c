int foo(int a, int b);

int clientmain() {
    c();
    b();
    foo(9,500);
	return a();
}

int a(){
    c();
    return b();
}

int b(){
    int i = 0;
    while (i < 100){
        i = i +5;
    }
    a();
    if (a() < 5)
        return c();
    else
        return 0;
}

void c(){
    a();
    return foo(9,500);
}
int foo (int a, int b) {
	int c=a+b;
	return c;
}
