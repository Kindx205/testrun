import random
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import requests
import pyautogui
import threading
from bs4 import BeautifulSoup
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2

# Configure undetected Chrome Driver with real user-agent
ua = UserAgent()
chrome_options = Options()
chrome_options.add_argument(f"--user-agent={ua.random}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Fetch multiple free proxies
proxy_sources = [
    "https://www.sslproxies.org/",
    "https://free-proxy-list.net/",
    "https://www.proxy-list.download/api/v1/get?type=https"
]

def get_free_proxies():
    proxies = []
    for url in proxy_sources:
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select("table tbody tr")
            for row in rows:
                columns = row.find_all("td")
                if len(columns) > 1:
                    proxy = f"{columns[0].text}:{columns[1].text}"
                    proxies.append(proxy)
        except:
            continue
    return proxies[:20]  # Fetch top 20 proxies

def is_proxy_working(proxy):
    try:
        test_url = "https://www.google.com"
        response = requests.get(test_url, proxies={"http": proxy, "https": proxy}, timeout=5)
        return response.status_code == 200
    except:
        return False

def rotate_proxy():
    proxy_list = get_free_proxies()
    for proxy in proxy_list:
        if is_proxy_working(proxy):
            return proxy
    return None

# Function to initialize driver with proper proxy settings
def get_driver(proxy):
    options = Options()
    options.add_argument(f"--user-agent={ua.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    return uc.Chrome(options=options)

# Simulate Google search with diverse queries
def simulate_google_search(driver, query, target_urls):
    driver.get("https://www.google.com")
    time.sleep(random.uniform(2, 4))
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    time.sleep(random.uniform(1, 3))  # Mimic real typing delay
    search_box.send_keys(Keys.RETURN)
    time.sleep(random.uniform(3, 6))
    
    links = driver.find_elements(By.CSS_SELECTOR, "h3")
    for link in links:
        try:
            parent = link.find_element(By.XPATH, "./ancestor::a")
            url = parent.get_attribute("href")
            for target_url in target_urls:
                if target_url in url:
                    driver.get(url)
                    return target_url
        except:
            continue
    return None

# Simulate realistic blog/article reading
def blog_reader(driver):
    total_scrolls = random.randint(15, 30)
    for _ in range(total_scrolls):
        scroll_height = random.uniform(0.1, 0.9) * driver.execute_script("return document.body.scrollHeight")
        driver.execute_script(f"window.scrollTo(0, {scroll_height})")
        time.sleep(random.uniform(5, 15))  # Realistic reading behavior
    
    if random.random() > 0.3:
        script = """
        var selection = window.getSelection();
        var range = document.createRange();
        var paragraphs = document.getElementsByTagName('p');
        if (paragraphs.length > 0) {
            var index = Math.floor(Math.random() * paragraphs.length);
            range.selectNodeContents(paragraphs[index]);
            selection.removeAllRanges();
            selection.addRange(range);
        }
        """
        driver.execute_script(script)
        time.sleep(random.uniform(3, 8))
    
    elements = driver.find_elements(By.TAG_NAME, "a")
    if elements:
        link = random.choice(elements)
        driver.execute_script("arguments[0].scrollIntoView();", link)
        time.sleep(random.uniform(3, 10))

# Solve Google reCAPTCHA
def solve_captcha(driver):
    solver = recaptchaV2()
    solver.set_verbose(1)
    solver.set_key("YOUR_ANTI_CAPTCHA_API_KEY")  # Replace with actual API key
    site_key = "EXTRACTED_SITE_KEY"  # Extract site key dynamically
    page_url = driver.current_url
    captcha_response = solver.solve_and_return_solution(page_url, site_key)
    if captcha_response:
        driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML='{captcha_response}';")
        time.sleep(2)
    
# Run test for a specific target
def run_test(target_url, visit_goal):
    visit_count = 0
    while visit_count < visit_goal:
        proxy = rotate_proxy()
        driver = get_driver(proxy)
        queries = ["best writing platforms", "HubPages top articles", "Vocal Media blog trends"]
        selected_target = simulate_google_search(driver, random.choice(queries), [target_url])
        if selected_target:
            solve_captcha(driver)
            blog_reader(driver)
            visit_count += random.randint(10, 30)
        driver.quit()
        time.sleep(random.uniform(60, 180))

# Run tests in parallel for HubPages and Vocal
def start_tests():
    threads = []
    visit_goal = 3000
    for site in ["hubpages.com", "vocal.media"]:
        thread = threading.Thread(target=run_test, args=(site, visit_goal,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

# Start the parallel tests
start_tests()
