
from selenium import webdriver
from selenium.webdriver.support.ui import Select

driver = webdriver.Firefox(executable_path="./geckodriver")
driver.get("http://stackoverflow.com/tags")
totalPages = int(driver.find_element_by_xpath("/html/body/div[4]/div[2]/div/div[3]/div[2]/a[5]").text)+1
file = open('tags.txt','w')
for page in range(776, totalPages):
    driver.get(f"https://stackoverflow.com/tags?page={page}&tab=popular")
    scrapTag = driver.find_elements_by_css_selector(".post-tag")
    for tag in scrapTag:
        tagName = tag.text
        print(tagName)
        file.write(tagName)
        file.write("\n")

file.close()