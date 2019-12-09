int main()
{
  int a;
  int b;
  foo(a, b);
}

int foo(int a, int b)
{
  int CLEVER_ret_0_old = 0;
  int CLEVER_ret_0_new = 0;
  int c_old = a + b;
  int c_new = b + a;
  CLEVER_ret_0_old = c_old;
  CLEVER_ret_0_new = c_new;
  assert(CLEVER_ret_0_old == CLEVER_ret_0_new);
}

