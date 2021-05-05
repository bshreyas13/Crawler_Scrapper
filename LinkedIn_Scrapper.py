# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 13:42:44 2021

@author: shrey


"""

##############################################################
## Script to navigate to a specific LinkedIn  profile       ##
## and scrape iformation relevant to a resume               ##
## Currently crawler is designed to search query            ##
## and nav to profile with first and last name              ##
## a few changes it can scrape more profiles                ##
############################################################## 

##Import requirements ##

import time
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import json
import argparse as ap

## Each Function is designed to perform a specific part of the process ##

## Logs into Likendin using saved credentials, navigates to my profile ##
## Also Scrolls through the page to load info ##
def LoginAndNav(username,password,query):
    ## Browser control using webdriver ##
    # Initialize the 'browser' using webdriver
    browser = webdriver.Chrome()
    
    # Get the login page for linkedin
    browser.get('https://www.linkedin.com/uas/login')

    # Username and Password for login
    user_pass = browser.find_element_by_id('username')
    user_pass.send_keys(username)

    user_pass = browser.find_element_by_id('password')
    user_pass.send_keys(password)

    user_pass.submit()
    time.sleep(5)

    # Nav to Profile Link to be scraped

    browser.get('https://www.linkedin.com/search/results/index/?keywords=' + query) 
    name = query.split()[0] + ' ' +query.split()[1]
    xpath = "(//span[text()='" + name + "'])" 
    time.sleep(10) 
    browser.find_element_by_xpath(xpath).click()
    ## Due to dynamic loading of the webpage 
    ## we need to load the entire webpage by scrolling
    # Pause before scrolling
    SCROLL_PAUSE_TIME = 6

    # Get the scroll height of the page
    last_height = browser.execute_script("return document.body.scrollHeight")

    for i in range(3):
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        time.sleep(SCROLL_PAUSE_TIME / 2)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight*(2/3));")
        time.sleep(SCROLL_PAUSE_TIME / 2)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
    return browser 

## Check If clickable drop downs are present and load info ##
def CheckDropDowns(browser):
    # try to expand sections(if available), else pass
    try:
        # click to expand education section
        education_expand_button = browser.find_element_by_xpath(
            "//section[@id='education-section']//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']")
        browser.execute_script("arguments[0].click();", education_expand_button)
    except:
        pass

    try:
        # click to expand projects section
        projects_expand_button = browser.find_element_by_xpath(
            "//div[@class='pv-accomplishments-block__content break-words']//button[@aria-label='Expand projects section' and @aria-expanded='false']")
        browser.execute_script("arguments[0].click();", projects_expand_button)
    except:
        pass

    try:
        # click to expand certifications section
        certifications_expand_button = browser.find_element_by_xpath(
            "//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']")
        browser.execute_script("arguments[0].click();", certifications_expand_button)
    except:
        pass

    try:
        # click to expand experience section
        experiences_expand_button = browser.find_element_by_xpath(
            "//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']")
        browser.execute_script("arguments[0].click();", experiences_expand_button)

        time.sleep(2)

        # inline-show-more-text__button link
        experiences_show_more_expand_button = browser.find_element_by_xpath("//button[@class='inline-show-more-text__button link']")
        # print(experiences_show_more_expand_button)
        browser.execute_script("arguments[0].click();", experiences_show_more_expand_button)
    except :
        pass

    try:
        # click to expand skills section
        skills_expand_button = browser.find_element_by_xpath(
            "//button[@class='pv-profile-section__card-action-bar pv-skills-section__additional-skills artdeco-container-card-action-bar artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--fluid']")
        browser.execute_script("arguments[0].click();", skills_expand_button)
    except :
        pass

    try:
        # click to expand volunteering section
        volunteer_expand_button = browser.find_element_by_xpath(
            "//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']")
        browser.execute_script("arguments[0].click();", volunteer_expand_button)
    except:
        pass
    
    try:
        # click to expand honors and awards section 
        honors_and_awards_expand_button = browser.find_element_by_xpath(
            "//section[@class='pv-profile-section pv-accomplishments-section artdeco-container-card ember-view']//button[@aria-label='Expand honors & awards section']")
        browser.execute_script("arguments[0].click();", honors_and_awards_expand_button)

        # click to expand honors and awards section to show more
        honors_and_awards_expand_button2 = browser.find_element_by_xpath(
            "//section[@class='pv-profile-section pv-accomplishments-section artdeco-container-card ember-view']//button[@aria-controls='honors-expandable-content' and @aria-expanded='false']")
        browser.execute_script("arguments[0].click();", honors_and_awards_expand_button2)
    except: 
        pass
    
## Scrapes Basic name info ##
def GetBasicInfo(soup,browser):

    basic_info = {}
    
    name_div = soup.find('div', {'class': 'flex-1 mr5 pv-top-card__list-container'})
    name_loc = name_div.find_all('ul')
    fullname = name_loc[0].find('li').get_text().strip()
    try:
        first_name, last_name = fullname.split()
    except:
        #Accounts for case with name as firstname, middlename, lastname
        first_name, middle_name, last_name = fullname.split()

    basic_info['first name'] = first_name
    basic_info['last name'] = last_name

    headline = name_div.find('h2').get_text().strip()
    basic_info['headline'] = headline
    basic_info['LinkedIn'] = browser.current_url

    
    # print(basic_info_list)
    return basic_info

## Scrapes Education Info ##
def GetEducation(soup):
    
    education_info_list =[]
    try:
        edu_section = soup.find('section', {'id': 'education-section'}).find('ul')
        edu_section = edu_section.find_all('li', {'class': "pv-profile-section__sortable-item pv-profile-section__section-info-item relative pv-profile-section__sortable-item--v2 pv-profile-section__list-item sortable-item ember-view"})
        college_names = []
        degree_names = []
        major_names = []
        grades = []
        dates = []
        for x in range(len(edu_section)):
            curr_section = edu_section[x]
            try:
                college_name = curr_section.find('h3', {'class': 'pv-entity__school-name t-16 t-black t-bold'})
                college_names.append(college_name.get_text())
            except:
                college_names.append('')

            try:
                degree_name = curr_section.find('p', {'class': 'pv-entity__secondary-title pv-entity__degree-name t-14 t-black t-normal'}).find('span', {
                    'class': 'pv-entity__comma-item'})
                degree_names.append(degree_name.get_text())
            except :
                degree_names.append('')

            try:
                major_name = curr_section.find('p', {'class': 'pv-entity__secondary-title pv-entity__fos t-14 t-black t-normal'}).find('span', {
                    'class': 'pv-entity__comma-item'})
                major_names.append(major_name.get_text())
            except:
                major_names.append('')
                
            try:
                grade = curr_section.find('p', {'class': 'pv-entity__secondary-title pv-entity__grade t-14 t-black t-normal'}).find('span', {
                    'class': 'pv-entity__comma-item'})
                grades.append(grade.get_text())
            except :
                grades.append('')

            try:
                time = curr_section.find('p', {'class': 'pv-entity__dates t-14 t-black--light t-normal'})
                dates.append((time.find_all('time')[1].get_text()))
            except:
                dates.append('')

        for i in range(len(edu_section)):
            education_info_list.append([college_names[i], degree_names[i], major_names[i], dates[i], grades[i]])
    except:
        # If no education added
        pass

    #print(education_info_list)
    return education_info_list

##Scrapes Experience ##
def GetExperience(soup):
    experience_info = {}
    list_items = []
    items = []

    try:
        experience_section = soup.find('section', {'class': 'experience-section'})
        # print(experience_section)

        list_items = experience_section.find('ul', {'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-more'})
    except :
        pass

    try:
        if list_items is None:
            list_items = experience_section.find('ul',
                                             {'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-no-more'})

        items = list_items.find_all('li', {'class': 'pv-entity__position-group-pager pv-profile-section__list-item ember-view'})
        company_names_list = []
        position_list = []
        dates_employed_list = []
        description_list = []

        for i in range(len(items)):
            try:
                curr_name = items[i].find('p', {'class': 'pv-entity__secondary-title t-14 t-black t-normal'})
                curr_name = curr_name.get_text().strip()
                curr_name = curr_name.split('\n')[0].strip()
                # print("1st currname", curr_name)
                company_names_list.append(curr_name)
            except :
                pass

            try:
                if curr_name is None:
                    curr_name = items[i].find('h3', {'class': 't-16 t-black t-bold'})
                    curr_name = curr_name.get_text().strip()
                    curr_name = curr_name.replace("Company Name\n", '')
                    company_names_list.append(curr_name)
            except:
                pass

            try:
                curr_position = items[i].find('h3', {'class': 't-16 t-black t-bold'})
                curr_position = curr_position.get_text().strip()
                position_list.append(curr_position)
            except:
                pass

            try:
                curr_dates = items[i].find('h4', {'class': 'pv-entity__date-range t-14 t-black--light t-normal'})
                curr_dates = curr_dates.get_text().strip()
                curr_dates = curr_dates.replace('Dates Employed\n', '')
                dates_employed_list.append(curr_dates)
            except:
                pass

            try:
                curr_description = items[i].find('div', {'class': 'pv-entity__extra-details t-14 t-black--light ember-view'})
                curr_description = curr_description.get_text().strip()
                curr_description = curr_description.replace('\n\n\n\n\n        see less', '')
                curr_description = curr_description.replace('\n\n   \n  \n\n\n\n\n\n\n\n\n\n', ' ')
                curr_description = curr_description.replace('\n\n    \n…\n\n        see more', '')
                curr_description = curr_description.replace('\n       ', '.')
                curr_description = curr_description.replace('\n\n', '.')
                description_list.append(curr_description)
            except:
                pass
                # Add empty description if no info
                description_list.append('')

        # Compile company_names_list from above data
        for i in range(len(company_names_list)):
            experience_info[company_names_list[i]] = {'postion':position_list[i], "dates":dates_employed_list[i], 'description':description_list[i]}

    except:
        # No Experience Added
        pass
    # print(experience_info_list)
    return experience_info


## Scrapes Projects ##
def GetProjects(soup):
    projects_info_list = []
    project_titles = []
    try:
        project_section = soup.find('div', {'id': 'projects-expandable-content'})
        project_section = project_section.find('ul', {'class': 'pv-accomplishments-block__list'})

        projects = project_section.find_all('h4', {'class': 'pv-accomplishment-entity__title t-14 t-bold'})

        for i in range(len(projects)):
            project_name = projects[i].get_text().split('\n')[2]
            project_name = re.sub(' +', ' ', project_name)
            project_titles.append(project_name.strip())

        projects = project_section.find_all('p', {'class': 'pv-accomplishment-entity__date t-14'})
        project_time = []
        for i in range(len(project_titles)):
            try:
                project_date = projects[i].get_text().split('\n')[1]
                project_date = re.sub(' +', ' ', project_date)
                project_time.append(project_date[1:])
            except:   
                project_time.append('')

        project_descriptions = []
        projects2 = project_section.find_all('p', {'class': 'pv-accomplishment-entity__description t-14'})
        for i in range(len(project_titles)):
            try:
                next_empty_elem = projects2[i].findNext('div')
                curr_proj_desc = next_empty_elem.next_sibling
                project_descriptions.append(curr_proj_desc.strip())
            except:
                project_descriptions.append('')

        # Construct projects_info_list from above data
        for i in range(len(project_titles)):
            projects_info_list.append([project_titles[i], project_time[i], project_descriptions[i]])
    except:
        pass
    # print(projects_info_list)
    return projects_info_list


## Scrapes Volunteering Info ##
def GetVolunteering(soup):
    volunteer_info_list = []
    items = []
    list_items = []
    try:
        volunteer_section = soup.find('section', {'class': 'pv-profile-section volunteering-section ember-view'})
        list_items = volunteer_section.find('ul', {
                'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-more ember-view'})
    except:
        pass

    try:
        if list_items is None:
            list_items = volunteer_section.find('ul',
                                        {'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-no-more'})
    except:
        pass

    try:
        items = list_items.find_all('li', {
            'class': 'pv-profile-section__sortable-item pv-profile-section__section-info-item relative pv-profile-section__sortable-item--v2 pv-profile-section__list-item sortable-item ember-view'})
    except:
        pass

    try:
        if items == []:
            items = list_items.find_all('li', {'class': 'pv-profile-section__list-item pv-volunteering-entity pv-profile-section__card-item ember-view'})
    except:
        pass

    try:
        for i in range(len(items)):
            curr_name = items[i].find('span', {'class': 'pv-entity__secondary-title'})
            curr_name = curr_name.get_text().strip()
            
            curr_role = items[i].find('h3', {'class': 't-16 t-black t-bold'})
            curr_role = curr_role.get_text().strip()

            try:
                curr_dates = items[i].find('h4', {'class': 'pv-entity__date-range detail-facet inline-block t-14 t-black--light t-normal'})
                curr_dates = curr_dates.get_text().strip()
                curr_dates = curr_dates.replace('Dates volunteered\n', '')
            except :
                curr_dates = ''

        try:
            curr_description = items[i].find('p', {'class': 'pv-entity__description t-14 t-normal mt4'})
            curr_description = curr_description.get_text().strip()
        except:
            curr_description = ''

        # Construct volunteer_info_list from above data
        volunteer_info_list.append([curr_name, curr_role, curr_dates, curr_description])

    except:
    # no volunteering added
        pass
    return volunteer_info_list

## Scrapes Top skills ##
def GetTopSkills(browser):

    #locate skills section
    skills = browser.find_elements_by_xpath("//*[starts-with(@class,'pv-skill-category-entity__name-text')]")

    #create skills set
    top_skills_list = []
    for skill in skills:
        top_skills_list.append(skill.text)
    return top_skills_list


## Scrapes Certs if any ##
def GetCertificates(soup):
    # certifications section
    certifications_info_list = []
    try:
        certificates_section = soup.find('section', {'id': 'certifications-section'})
        
        list_items = certificates_section.find('ul',
                                           {'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-more'})
    except :
        pass
    try:
        if list_items is None:
            list_items = certificates_section.find('ul', {
                'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-no-more'})

        items = list_items.find_all('li', {'class': 'pv-profile-section__sortable-item pv-certification-entity ember-view'})
        cert_names_list = []
        cert_issuer_list = []
        cert_dates_list = []

        for i in range(len(items)):
            curr_cert_name = items[i].find('h3', {'class': 't-16 t-bold'})
            curr_cert_name = curr_cert_name.get_text().strip()
            cert_names_list.append(curr_cert_name)
            
            curr_issuer_name = items[i].find_all('p', {'class': 't-14'})[0]
            curr_issuer_name = curr_issuer_name.get_text().strip()
            curr_issuer_name = curr_issuer_name.replace('Issuing authority\n', '')
            cert_issuer_list.append(curr_issuer_name)

            curr_cert_date = items[i].find_all('p', {'class': 't-14'})[1]
            curr_cert_date = curr_cert_date.get_text().strip()
            curr_cert_date = curr_cert_date.replace('Issued date and, if applicable, expiration date of the certification or license\n', '').replace(
                'No Expiration Date', '').replace('Issued ', '')
            cert_dates_list.append(curr_cert_date)

    # adding elements in certifications_info_list as per schema
        for i in range(len(cert_names_list)):
            certifications_info_list.append([cert_names_list[i], cert_dates_list[i], cert_issuer_list[i]])

    except :
    # no certificates added
        pass

    # print(certifications_info_list)
    return certifications_info_list

if __name__ == '__main__':
    
    parser = ap.ArgumentParser()
    parser.add_argument("-u","--username", required = True, help = "LinkedIn username")
    parser.add_argument("-p","--password", required = True, help = "LinkedIn password")
    parser.add_argument("-sq","--search_query", required = True, help = "query words to search profile on LinkendIn")
    args = vars(parser.parse_args())

    username = args['username']
    password = args['password']
    query = args['search_query']
    browser = LoginAndNav(username,password,query)
    CheckDropDowns(browser)
    # use beautiful soup for html parsing
    src = browser.page_source
    soup = BeautifulSoup(src, 'html.parser')
    basic_info = GetBasicInfo(soup,browser)
    education_info = GetEducation(soup)
    projects_info = GetProjects(soup)
    experience_info = GetExperience(soup)
    volunteer_info = GetVolunteering(soup)
    top_skills_list = GetTopSkills(browser)
    
    ## No certifications added in my profile 
    ##however this scrapes in case there are certs
    certifications_info = GetCertificates(soup)

    ## Test Prints ##
    # print (basic_info)
    # print(education_info)
    # print(projects_info)
    # print(experience_info)
    # print(volunteer_info)
    # print(top_skills_list)
    # print (certifications_info)
    
    
    ## Close the browser once scraping is done
    browser.close()


    final_all_lists = [basic_info, education_info, projects_info, certifications_info, experience_info, top_skills_list,
                       volunteer_info]
    
    json_data = {'Basic_info': basic_info, 'Education': education_info, 'Projects': projects_info,
                 'Certifications': certifications_info, 'Experience': experience_info, 'Top skills': top_skills_list,
                 'Volunteering': volunteer_info }
    
    final_json = json.dumps(json_data, indent=4)
    print(final_json)
    file = open("scraped_data.json", 'w')
    file.writelines(final_json)
    file.close()

