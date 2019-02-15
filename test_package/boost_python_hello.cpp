#include <boost/python.hpp>

char const* greet()
{
   return "hello, world!!!!!";
}

BOOST_PYTHON_MODULE(boost_python_hello)
{
    using namespace boost::python;
    def("greet", greet);
}
