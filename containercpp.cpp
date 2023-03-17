#include <iostream>
#include <dirent.h>
#include <map>
#include <boost/filesystem.hpp>
#include <boost/filesystem/fstream.hpp>
#include <fstream>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/json/value.hpp>
#include <boost/json/parse.hpp>
#include <string>
#include <boost/iostreams/filtering_streambuf.hpp>
#include <boost/iostreams/copy.hpp>
#include <boost/iostreams/filter/gzip.hpp>
#include <boost/archive/iterators/base64_from_binary.hpp>
#include <boost/archive/iterators/binary_from_base64.hpp>
#include <boost/archive/iterators/transform_width.hpp>
#include <boost/archive/iterators/insert_linebreaks.hpp>
#include <boost/archive/iterators/remove_whitespace.hpp>
#include <algorithm>

using namespace boost::filesystem;
using namespace std;
namespace pt = boost::property_tree;

class container
{
    string docker_home = "/var/snap/docker/common/var-lib-docker/containers";
    string data_file = "config.v2.json";

    public:
    void extract_data();
};

