from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import random

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo = 1000,
    )
    open_robot_order_website()
    orders = get_order()
    fill_the_form(orders)

def open_robot_order_website():
    """Connect to website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    """Select any one of the prompt except 'No way!'"""
    page = browser.page()
    choice = random.randrange(1,3)
    button = ["button:text('OK')","button:text('Yep')","button:text('I guess so...')"]
    page.click(button[choice])

def get_order():
    """Download the orders file, read it as a table, and return the result"""
    http = HTTP()
    http.download(url ="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    table = Tables()
    data = table.read_table_from_csv("orders.csv", header=True)
    return data

def fill_the_form(data):
    """Fill the order form and export receipt as pdf"""
    for record in data:
        close_annoying_modal()
        page = browser.page()
        page.select_option('//*[@id="head"]', str(record['Head']))
        page.click('//*[@id="id-body-{}"]'.format(str(record['Body'])))
        page.fill("[placeholder='Enter the part number for the legs']", record['Legs'])
        # page.fill("[id='1713712001487']", record['Legs'])
        page.fill('//*[@id="address"]', record['Address'])
        preview_robot(record)
        submit_order()
        pdf_file = store_receipt_as_pdf(record['Order number'])
        screenshot = screenshot_robot(record['Order number'])
        embed_screenshot_to_receipt(screenshot, pdf_file)
        next_order()
        archive

def preview_robot(record):
    """Preview the order"""
    page = browser.page()
    page.click("button:text('Preview')")
    # robot_html = page.locator('//*[@id="robot-preview-image"]')
    # head_html = page.locator('//*[@id="robot-preview-image"]/img[record["Head"]]')
    # body_html = page.locator('//*[@id="robot-preview-image"]/img[record["Body"]]')
    # legs_html=page.locator('//*[@id="robot-preview-image"]/img[record["Legs"]]')

def submit_order():
    """Submit Order or Try again"""
    page = browser.page()
    while (True):
        try:
            page.click('//*[@id="order"]')
        except:
            print("Order cannot be submitted! Trying again.")
            continue

def store_receipt_as_pdf(order_number) -> str:
    """Receipt is saved as pdf"""
    page = browser.page()
    receipt_html = page.locator('#receipt').inner_html()
    pdf = PDF()
    path = f"output/receipts/receipt{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, path)
    return str(path)
    

def screenshot_robot(order_number) -> str:
    """Screenshots the robot"""
    page = browser.page()
    path = f'output/screenshots/screenshot{order_number}.png'
    image_loc = page.locator('//*[@id="robot-preview-image"]')
    page.screenshot(image_loc, path = path)
    return str(path)

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(files = screenshot, target_document = pdf_file, append=True)


def next_order():
    page = browser.page()
    page.click("button:text('ORDER ANOTHER ROBOT')")

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts','output/receipt.zip')





