#!/usr/bin/python
# -*- coding: UTF-8 -*-
# make by davidchen
# the util function is make xml to lua struct
import xml.etree.cElementTree as ET
import os,shutil,sys

idkeys=["id","ident"]

class Node:
    def __init__(self,attrs,tag):
        self.children = dict()
        self.attrs = attrs
        self.tag = tag
        self.gap = "    "
    
    def InsertChild(self,child):
        if not self.children.has_key(child.tag):
            self.children[child.tag] = []
        self.children[child.tag].append(child)
        
    def SetTag(self,tag):
        self.tag = tag
        
    def ReturnSpecialKey(self):
        for index in range(len(idkeys)):
            if self.attrs.has_key(idkeys[index]):
                return idkeys[index],self.attrs[idkeys[index]]
        return None,-1
        
    #layer decide the number of self.gap
    #index means the node index in children list
    def ToString(self,isRoot,index,layer):
        res = ""
        tabStr = ""
        
        if isRoot:
            res = self.tag+" = {\n"
        else:
            keyName = None
            keyValue = -1
            if len(self.attrs) > 0:
                keyName,keyValue = self.ReturnSpecialKey()
            for i in range(layer):
                tabStr += self.gap
            if keyName == None:
                res = tabStr+"["+str(index)+"] = {\n"
            else:
                res = tabStr+"["+str(keyValue)+"] = {\n"
        layer = layer + 1
        subTabStr = tabStr+self.gap
        for key in self.attrs:
            if self.attrs[key].isdigit():
                res += subTabStr+key+"="+self.attrs[key]+",\n"
            else:
                res += subTabStr+key+"="+"\""+self.attrs[key]+"\",\n"
        for key in self.children:
            childList = self.children[key]
            if len(childList) > 0:
                res += subTabStr+key+" = {\n"
                for idx in range(len(childList)): 
                    res += childList[idx].ToString(False,idx+1,layer+1)
                res += subTabStr+"}\n"
        res += tabStr+"},\n"
        return res

class XML2Lua:
    
    def __init__(self,fromPath,destPath):
        self.fromPath = fromPath
        self.destPath = destPath
        
    def CreateDirs(self,path,isFile):
        destDir = path
        if isFile:
            path = path.replace("\\","/")
            pos = path.rfind("/")
            destDir = path[0:pos]
        if os.path.exists(destDir) == False:
            os.makedirs(destDir)
            
    def DoConvert(self):
        for maindir, subdir, file_name_list in os.walk(self.fromPath):
            for filename in file_name_list:
                apath = os.path.join(maindir, filename)
                ext = os.path.splitext(apath)[1] 
                if ext == ".xml":
                    xmlNode = self.ReadXML(apath)
                    temp = apath.replace(self.fromPath,"")
                    exportFile = self.destPath+temp
                    exportFile = exportFile.replace(ext,".lua")
                    self.ExportToFile(exportFile,xmlNode)
    
    def ReadXML(self,path):
        try:
            tree = ET.ElementTree(file=path)
        except Exception as e:
            print("convert "+path+" error:"+e.message)
            return
        root = tree.getroot()
        
        rootNode = Node(root.attrib,root.tag)
        self.HandlerNode(root,rootNode)
        return rootNode
        
    def HandlerNode(self,node,parentNode):
        for child in node:
            tempNode = Node(child.attrib, child.tag)
            parentNode.InsertChild(tempNode)
            if len(child.getchildren()) > 0:
                self.HandlerNode(child,tempNode)
                
    def PrintInfo(self):
        print(self.rootNode.ToString(True,0,0))
        
    def ExportToFile(self,path,node):
        if node == None:
            return
        res = node.ToString(True,0,0)
        self.CreateDirs(path,True)
        res = res.encode("utf-8")
        f = open(path, "w")
        f.write(res)
        f.close()
        print(path+" convert to lua complete!")
        
select = raw_input("Select one mode:\n \
      1.Convert a file to lua\n \
      2.Convert all files in a folder\n")
if select == "1":
    xmlFile = raw_input("Input xml file path:\n")
    luaFile = raw_input("Input export lua file path:\n")
    temp = XML2Lua(None,None)
    xmlNode = temp.ReadXML(xmlFile)
    temp.ExportToFile(luaFile,xmlNode)
elif select == "2":
    fromFolder = raw_input("Input xml folder path:\n")
    destFolder = raw_input("Input export lua folder path:\n")
    temp = XML2Lua(fromFolder,destFolder)
    temp.DoConvert()
      