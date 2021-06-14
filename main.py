# # This is a sample Python script.
#
# # Press Shift+F10 to execute it or replace it with your code.
# # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
#
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from databaseConnect import databaseConnect


def userDetails(obj):
    '''
    fuction to extract the user details and insert it into the db
    '''
    userID = int(obj.find_element_by_css_selector(".user-details a").get_attribute("href").split('/')[4])
    userName = obj.find_element_by_css_selector('.user-details a').text
    reputation = obj.find_element_by_css_selector('.user-details .reputation-score').text
    gold = silver = bronze = 0
    try:
        try:
            gold = int(obj.find_element_by_css_selector('.user-details > div').find_element_by_xpath(
                "span/span[@class='badge1']/following-sibling::span").text)
        except NoSuchElementException:
            pass
        try:
            silver = int(obj.find_element_by_css_selector('.user-details > div').find_element_by_xpath(
                "span/span[@class='badge2']/following-sibling::span").text)
        except NoSuchElementException:
            pass
        try:
            bronze = int(obj.find_element_by_css_selector('.user-details > div').find_element_by_xpath(
                "span/span[@class='badge3']/following-sibling::span").text)
        except NoSuchElementException:
            pass
    except(AttributeError, TypeError):
        pass
    finally:
        userInsert = f"INSERT or IGNORE INTO user (userID, userName, reputationScore, gold, silver, bronze) VALUES({userID},\'{userName}\',\'{reputation}\',{gold},{silver},{bronze})"
        insertObject = databaseConnect(userInsert)
        insertObject.execute()


def commentDetails(obj, flag):
    '''
    fucntion to extract the detials of the comment and insert it into the db
    '''
    comment = obj.find_elements_by_css_selector('.js-post-comments-component .comments')
    for com in comment:
        ID = int(obj.find_element_by_class_name('comments').get_attribute('data-post-id'))
        try:
            comText = com.find_elements_by_css_selector(".comment")
            for a in comText:
                comID = int(a.get_attribute("data-comment-id"))
                comText = a.find_element_by_css_selector(".comment-copy").text.replace('\n', '').replace('\'',
                                                                                                         '*').replace(
                    '\"', '*')
                userName = a.find_element_by_css_selector(".comment-user").get_attribute("href").split('/')[5]
                commentTime = \
                a.find_element_by_css_selector(".comment-date .comment-link span").get_attribute("title").split(',')[0]
                if flag == 0:
                    commentInsertQ = f"INSERT INTO commentQuestions (commentID,comment,userName,questionID,time) VALUES({comID},\'{comText}\',\'{userName}\',{ID},\'{commentTime}\')"
                    insertObject = databaseConnect(commentInsertQ)
                    insertObject.execute()
                else:
                    commentInsertA = f"INSERT INTO commentAnswers (commentAnsID,comment,userName,answerID,time) VALUES({comID},\'{comText}\',\'{userName}\',{ID},\'{commentTime}\')"
                    insertObject = databaseConnect(commentInsertA)
                    insertObject.execute()
        except NoSuchElementException:
            pass


tagInput = input("Enter the tag:")
fileTag = open("tags.txt", "r")
readfile = fileTag.read()
driver = webdriver.Firefox(executable_path="./geckodriver")
if tagInput in readfile:
    driver.get('https://stackoverflow.com/questions/tagged/' + tagInput + '?tab=newest&pagesize=50')
    questionsPgSize = driver.find_elements_by_css_selector(".question-summary")
    questionLinks = []
    for question in questionsPgSize:
        quest = question.find_element_by_css_selector(".question-hyperlink")
        questionLink = str(quest.get_attribute("href"))
        questionLinks.append(questionLink)
    for link in questionLinks:
        driver.get(link)
        quest = driver.find_element_by_css_selector(".question-hyperlink")
        questionLink = str(quest.get_attribute("href"))
        questionID = int(quest.get_attribute("href").split('/')[4])
        questionTitle = quest.text.replace('\'', '*').replace('\"', '*')
        votes = int(driver.find_element_by_css_selector('.js-vote-count').text)

        views = driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div[2]/div[3]').text.replace(' ',
                                                                                                         '').replace(
            'Viewed', '').replace('times', '')
        time = driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div[2]/div[1]').get_attribute("title")
        try:
            noOfAnswers = int(
                driver.find_element_by_css_selector('#answers-header > div > div.grid--cell.fl1 > h2').text.replace(
                    'Answers', '').replace(' ', ''))
        except ValueError:
            noOfAnswers = 0
        userID = int(driver.find_element_by_css_selector(".user-details a").get_attribute("href").split('/')[4])
        userDetails(driver)

        tagQuestion = driver.find_elements_by_css_selector('.post-taglist > .grid > a')

        for tag in tagQuestion:
            tagName = str(tag.text).replace('\n', '').split(' ')
            for tag in tagName:
                tagInsert = f"INSERT or IGNORE INTO tags (tagName) VALUES ('{tag}')"
                insertObject = databaseConnect(tagInsert)
                insertObject.execute()
            for tag in tagName:
                tagIDExtract = f"SELECT tagID FROM tags WHERE tagName = '{tag}'"
                selectObject = databaseConnect(tagIDExtract)
                tagID = selectObject.execute()
                mapInsert = f"INSERT or IGNORE INTO map (tagID, questionID) VALUES ({tagID[0][0]},{questionID})"
                insertObject1 = databaseConnect(mapInsert)
                insertObject1.execute()

        questionD = driver.find_element_by_css_selector('.postcell > div')
        description = questionD.text.replace('\n', '').replace('\'', '*').replace('\"', '*')

        questionInsert = f"INSERT or IGNORE INTO question (questionID, votes, views, userID, description, noOfAnswers, time, title, questionLink) VALUES ({questionID},{votes},\'{views}\',{userID},\'{description}\',{noOfAnswers},\'{time}\',\'{questionTitle}\',\'{questionLink}\')"
        insertObject2 = databaseConnect(questionInsert)
        insertObject2.execute()

        questionFlag = 0
        questionComment = driver.find_element_by_class_name('js-post-comments-component')
        commentDetails(questionComment, questionFlag)
        noOfAnswers = 1
        if noOfAnswers > 0:
            listOfAnswers = driver.find_elements_by_css_selector(".answer")
            for answer in listOfAnswers:
                answerID = int(answer.get_attribute("id").split('-')[1])
                noOfUpvotes = isAccepted = 0
                try:
                    answerD = answer.find_element_by_css_selector('.answercell > div')
                    description = answerD.text.replace('\n', '').replace('\'', '*').replace('\"', '*')
                    answerTime = answer.find_element_by_css_selector(".relativetime").get_attribute("title")
                    userID = int(
                        answer.find_element_by_css_selector(".user-details a").get_attribute("href").split('/')[4])
                    noOfUpvotes = int(answer.find_element_by_class_name('js-vote-count').text)
                    accepted = answer.find_element_by_class_name('js-accepted-answer-indicator').get_attribute(
                        "aria-label")
                    if accepted == 'Accepted':
                        isAccepted = 1
                    userDetails(answer)
                except TypeError:
                    pass
                finally:
                    answerInsert = f"INSERT or IGNORE INTO answer (answerID,noOfUpvotes,userID,questionID,time,description,accepted) VALUES({answerID},{noOfUpvotes},{userID},{questionID},\'{answerTime}\',\'{description}\',{isAccepted})"
                    insertObject3 = databaseConnect(answerInsert)
                    insertObject3.execute()
                    answerFlag = 1
                    commentDetails(answer, answerFlag)
