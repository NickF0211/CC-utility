int foo(int a, int b);

int main(void) {
    int x = nondet_int();
    int y = nondet_int();
    assert(foo_old(x, y) == foo_new(x,y));
}

int foo_old(int a, int b) {
	int c=a+b;
	return c;
}


int foo_new(int a, int b) {
	int c=b+a;
	return c;
}
