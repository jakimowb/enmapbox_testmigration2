from qgis.PyQt.QtCore import *
from qgis.PyQt.QtXml import *
from qgis.PyQt.QtNetwork import *
from qgis.core import *
from pyplugin_installer import installer, installer_data
from pyplugin_installer.version_compare import isCompatible, pyQgisVersion
reply = QgsNetworkAccessManager.instance().get(installer_data.repositories.mRepositories['tesschr']['QRequest'])
reposName = reply.property('reposName')
content = reply.readAll()
reposXML = QDomDocument()
a = QByteArray()
a.append("& ")
b = QByteArray()
b.append("&amp; ")
content = content.replace(a, b)
reposXML.setContent(content)
pluginNodes = reposXML.elementsByTagName("pyqgis_plugin")

if pluginNodes.size():
    for i in range(pluginNodes.size()):
        fileName = pluginNodes.item(i).firstChildElement("file_name").text().strip()
        if not fileName:
            fileName = QFileInfo(
                pluginNodes.item(i).firstChildElement("download_url").text().strip().split("?")[0]).fileName()
        name = fileName.partition(".")[0]
        experimental = False
        if pluginNodes.item(i).firstChildElement("experimental").text().strip().upper() in ["TRUE", "YES"]:
            experimental = True
        deprecated = False
        if pluginNodes.item(i).firstChildElement("deprecated").text().strip().upper() in ["TRUE", "YES"]:
            deprecated = True
        trusted = False
        if pluginNodes.item(i).firstChildElement("trusted").text().strip().upper() in ["TRUE", "YES"]:
            trusted = True
        icon = pluginNodes.item(i).firstChildElement("icon").text().strip()
        if icon and not icon.startswith("http"):
            #icon = "http://{}/{}".format(QUrl(self.mRepositories[reposName]["url"]).host(), icon)
            pass

        if pluginNodes.item(i).toElement().hasAttribute("plugin_id"):
            plugin_id = pluginNodes.item(i).toElement().attribute("plugin_id")
        else:
            plugin_id = None

        plugin = {
            "id": name,
            "plugin_id": plugin_id,
            "name": pluginNodes.item(i).toElement().attribute("name"),
            "version_available": pluginNodes.item(i).toElement().attribute("version"),
            "description": pluginNodes.item(i).firstChildElement("description").text().strip(),
            "about": pluginNodes.item(i).firstChildElement("about").text().strip(),
            "author_name": pluginNodes.item(i).firstChildElement("author_name").text().strip(),
            "homepage": pluginNodes.item(i).firstChildElement("homepage").text().strip(),
            "download_url": pluginNodes.item(i).firstChildElement("download_url").text().strip(),
            "category": pluginNodes.item(i).firstChildElement("category").text().strip(),
            "tags": pluginNodes.item(i).firstChildElement("tags").text().strip(),
            "changelog": pluginNodes.item(i).firstChildElement("changelog").text().strip(),
            "author_email": pluginNodes.item(i).firstChildElement("author_email").text().strip(),
            "tracker": pluginNodes.item(i).firstChildElement("tracker").text().strip(),
            "code_repository": pluginNodes.item(i).firstChildElement("repository").text().strip(),
            "downloads": pluginNodes.item(i).firstChildElement("downloads").text().strip(),
            "average_vote": pluginNodes.item(i).firstChildElement("average_vote").text().strip(),
            "rating_votes": pluginNodes.item(i).firstChildElement("rating_votes").text().strip(),
            "icon": icon,
            "experimental": experimental,
            "deprecated": deprecated,
            "trusted": trusted,
            "filename": fileName,
            "installed": False,
            "available": True,
            "status": "not installed",
            "error": "",
            "error_details": "",
            "version_installed": "",
            "zip_repository": reposName,
            "library": "",
            "readonly": False
        }
        qgisMinimumVersion = pluginNodes.item(i).firstChildElement("qgis_minimum_version").text().strip()
        if not qgisMinimumVersion:
            qgisMinimumVersion = "2"
        qgisMaximumVersion = pluginNodes.item(i).firstChildElement("qgis_maximum_version").text().strip()
        if not qgisMaximumVersion:
            qgisMaximumVersion = qgisMinimumVersion[0] + ".99"
        # if compatible, add the plugin to the list
        if not pluginNodes.item(i).firstChildElement("disabled").text().strip().upper() in ["TRUE", "YES"]:
            if isCompatible(pyQgisVersion(), qgisMinimumVersion, qgisMaximumVersion):
                # add the plugin to the cache
                print('OK')
                print(plugin)
            else:
                print('INVALID2')
                print(plugin)
        else:
            print('INVALID1')
            print(plugin)

