

class XpathCollection:

    #Login Page
    user = "gwt-TextBox"
    pwd = "gwt-PasswordTextBox"
    login_list = "gwt-ListBox"
    login = "gwt-Button"

    #Bulk Page
    logout = "//td[2]/button"
    pattern_box = "searchPattern"
    language_list = "//select"
    queue_list = "//td[4]/div/select"
    security_queues_only = "//input[@id='gwt-uid-16']"
    per_page_list = "//td[6]/div/select"
    priority = "//td[3]/div/input"
    search = "//button[@type='button']"
    cat1 = "//div[2]/table/tbody/tr/td[2]/div/select"
    cat2 = "//select[2]"
    comment_box = "//textarea[@name='actionComments']"
    bulk_action = "//td[3]/select"
    submit = "//td[4]/button"
    select_all = "//input[@type='checkbox']"
    check_box_1 = "//div/table/tbody/tr/td/div/input"
    cb_1 = "//tr["
    cb_2 = "]/td/div/input"
    dismiss = "(//button[@type='button'])[2]"
    url_col_1 = "//tr["
    url_col_2 = "]/td[2]/div"
    first_url_row = "//div[2]/div/div/table/tbody/tr/td[2]/div"
    first_lang_row = "//div[2]/div/div/table/tbody/tr/td[3]/div"
    first_covered_row = "//div/table/tbody/tr/td[4]/div"
    lang_col_1 = "//tr["
    lang_col_2 = "]/td[3]/div"
    first_priority_row = "//div/table/tbody/tr/td[5]/div"
    priority_1 = "//tr["
    priority_2 = "]/td[5]/div"
    #css selector
    no_urls = "//div[2]/div/div/table/tbody/tr/td/div"
    log_in_user = "//div[5]/div/div[2]/table/tbody/tr/td/div"


class Domip:
    """DOMIP xpath collection"""
    text_box = "//input[@type='text']"
    go = "//button[@type='button']"
    update = "//table[2]/tbody/tr/td[2]/button"
    reset = "//table[2]/tbody/tr/td/button"
    ip_box = "//td[2]/input"
    row_1 = "//div[3]/div/div[2]/div/div/table/tbody/tr/td/div"
    row_2 = "//tr[2]/td/div/a"
    select_option = "Domain IP"
