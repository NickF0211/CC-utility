int main()
{
  int a;
  int b;
  foo(a, b);
}

int foo(int a, int b)
{
  int ret_0_old = 0;
  int ret_0_new = 0;
  int c_old = a + b;
  int c_new = b + a;
  ret_0_old = c_old;
  ret_0_new = c_new;
  assert(ret_0_old == ret_0_new);
}

