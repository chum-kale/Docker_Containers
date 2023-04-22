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
#include <sstream>

using namespace boost::filesystem;
using namespace std;
namespace pt = boost::property_tree;

class container
{
    string docker_home = "/var/snap/docker/common/var-lib-docker/";
    string container_path = (docker_home + "containers/");
    string data_file = "config.v2.json";

public:
    void extract_data(string container_id);
};

void container::extract_data(string container_id)
{
    //string new_path = container_path + container_id + "/config.v2.json/";
    if (is_directory(container_path))
    {
        DIR *dir;
        struct dirent *ent;
        dir = opendir(container_path.c_str());
        pt::ptree root;
        std::string full_container_id;
        while ((ent = readdir(dir)) != NULL)
        {
            //cout<<"bp1"<<endl;
            string new_path = container_path + container_id + "/config.v2.json";
            if (is_regular_file(new_path))
            {
                std::ifstream ifs(new_path);
                std::string container_info((std::istreambuf_iterator<char>(ifs)), (std::istreambuf_iterator<char>()));
                pt::read_json(new_path, root);
                full_container_id = root.get<std::string>("ID");
                string mount_id_file = (docker_home + "image/overlay2/layerdb/mounts/" + full_container_id + "/mount-id");
                //cout<<"bp2"<<endl;
                if (is_regular_file(mount_id_file))
                {
                    std::ifstream ifs(mount_id_file);
                    std::string mount_id((std::istreambuf_iterator<char>(ifs)), (std::istreambuf_iterator<char>()));
                    string lower_dir_file = (docker_home + "overlay2/" + mount_id + "/lower");
                    std::string token;
                    std::vector <std::string> lower_dir;
                    if (is_regular_file(lower_dir_file))
                    {
                        std::ifstream con(lower_dir_file);
                        std::string lower_id_symlinks((std::istreambuf_iterator<char>(con)), (std::istreambuf_iterator<char>()));
                        std::stringstream ss(lower_id_symlinks);
                        while (getline(ss, token, ':'))
                        {
                            lower_dir.push_back(token); 
                        }
                        for (std::string str : lower_dir)
                        {
                            cout << str << " ";
                        }
                    }
                }
            }
        }
    }
}
    

int main()
{
    container c1;
    string container_data;
    cout << "Enter container id:" << endl;
    cin >> container_data;
    c1.extract_data(container_data);
}