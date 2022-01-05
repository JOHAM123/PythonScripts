# from googletrans import Translator, constants
# from pprint import pprint
import os;
# translator = Translator()

# from googletrans import Translator

# translator = Translator(raise_exception=True)
# translation = translator.translate("研修会資料", src='japanese', dest="en")
# print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")

# from yandex.Translater import Translater
# tr = Translater()
# tr.set_key('yandex_key') # Api key found on https://translate.yandex.com/developers/keys
# tr.set_from_lang('en')
# tr.set_to_lang('ru')
# tr.translate()


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



# browser = webdriver.Chrome()

# browser.get('https://translate.google.co.jp/?sl=ja&tl=en&text="ドキュメント"&op=translate')  
# browser.implicitly_wait(100)
# element = browser.find_element(By.CLASS_NAME, "NqnNQd")
  
# # print complete element
# divs = browser.find_element(By.CLASS_NAME, "NqnNQd")
# print(divs.get_attribute('innerHTML'))


# browser.quit()

        # os.rename(os.path.join(root, name), os.path.join(root, translation.text))

# os.chdir("C:/Users/dynam/Desktop/glex/ドキュメント/00_GRANDIT研修会資料/1日目/参考資料")
# print(os.getcwd())
# https://translate.google.co.jp/?sl=ja&tl=en&text="ドキュメント"&op=translate
# document.getElementsByClassName("NqnNQd")[0].innerHTML;

# #Walk the directory and change the file names and folder names in all folders and subfolders.

# for root, dirs, files in os.walk("C:/Users/dynam/Desktop/glex/ドキュメント/00_GRANDIT研修会資料/1日目/参考資料", topdown=False):
#    for file_name in files:
#       translation = translator.translate(file_name, dest="en")
#       print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
#       new_name = translation.text
#       if (new_name != file_name):
#          os.rename(os.path.join(root, file_name), os.path.join(root, new_name))

#    for dir_name in dirs:
#       translation = translator.translate(dir_name, dest="en")
#       print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
#       new_name = translation.text
#       if (new_name != dir_name):
#          os.rename(os.path.join(root, dir_name), os.path.join(root, new_name))

def translate_string(val_string, lang):
    browser = webdriver.Chrome()

    browser.get('https://translate.google.co.jp/?sl=ja&tl=en&text="'+val_string+'"&op=translate')  
    browser.implicitly_wait(100)    
    divs = browser.find_element(By.CLASS_NAME, "NqnNQd")
    val_string = divs.get_attribute('innerHTML')
    val_string = val_string.lstrip()
    val_string = val_string.lower()
    val_string = val_string.replace("\\","_")
    val_string = "".join(val_string.split())
    browser.quit()

    return val_string



    
def translate_folder_and_files_name(folder_path, lang):
    for root, dirs, files in os.walk(folder_path, topdown=False):
       for file_name in files:
          translation = translate_string(file_name, lang)
          new_name = translation
          print("\n-->"+(root +"/"+new_name))
          root = root.replace("\\","/")
          src = (root +"/"+ file_name)
          dest = (root+"/"+new_name)
          if (new_name != file_name):
             os.rename(src.replace("\"",""), dest.replace("\"",""))

       for dir_name in dirs:
          translation = translate_string(dir_name, lang)
          new_name = translation
          root = root.replace("\\","/")
          src = (root +"/"+ dir_name)
          dest = (root+"/"+new_name)
          print("\n-->"+(root+"/"+new_name))
          if (new_name != dir_name):
             os.rename(src.replace("\"",""), dest.replace("\"",""))

def main():
    folder_path = "C:/Users/dynam/Desktop/glex"
    lang = "en"
    translate_folder_and_files_name(folder_path, lang)
    

main()