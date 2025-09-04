"""
Playwright 异步教学案例
展示Playwright的基本操作，包括页面导航、元素交互、数据获取等
"""

import asyncio
from playwright.async_api import async_playwright


async def basic_navigation_example():
    """基本页面导航和信息获取示例"""
    print("🚀 开始基本页面导航示例...")
    
    async with async_playwright() as p:
        # 启动浏览器（可选择 chromium, firefox, webkit）
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 导航到网页
        await page.goto("https://example.com")
        print(f"页面标题: {await page.title()}")
        print(f"页面URL: {page.url}")
        
        # 获取页面内容
        content = await page.content()
        print(f"页面内容长度: {len(content)} 字符")
        
        await browser.close()
    print("✅ 基本页面导航示例完成\n")


async def element_interaction_example():
    """元素交互示例"""
    print("🎯 开始元素交互示例...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 访问搜索页面
        await page.goto("https://www.bing.com")
        
        # 等待搜索框加载
        search_box = page.locator('input[name="q"]')
        await search_box.wait_for()
        
        # 输入搜索内容
        await search_box.fill("Playwright Python")
        print("已输入搜索关键词")
        
        # 点击搜索按钮
        search_button = page.locator('input[type="submit"]')
        await search_button.click()
        
        # 等待搜索结果加载
        await page.wait_for_selector('.b_algo')
        print("搜索结果已加载")
        
        # 获取第一个搜索结果的标题
        first_result = page.locator('.b_algo').first
        title = await first_result.locator('h2').text_content()
        print(f"第一个搜索结果标题: {title}")
        
        await browser.close()
    print("✅ 元素交互示例完成\n")


async def form_handling_example():
    """表单处理示例"""
    print("📝 开始表单处理示例...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 创建一个简单的HTML表单进行测试
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>测试表单</title></head>
        <body>
            <h1>用户信息表单</h1>
            <form id="userForm">
                <label>姓名: <input type="text" id="name" name="name"></label><br><br>
                <label>邮箱: <input type="email" id="email" name="email"></label><br><br>
                <label>年龄: <input type="number" id="age" name="age"></label><br><br>
                <label>性别: 
                    <select id="gender" name="gender">
                        <option value="">请选择</option>
                        <option value="male">男</option>
                        <option value="female">女</option>
                    </select>
                </label><br><br>
                <label><input type="checkbox" id="agree" name="agree"> 同意条款</label><br><br>
                <button type="submit">提交</button>
            </form>
        </body>
        </html>
        """
        
        # 设置页面内容
        await page.set_content(html_content)
        
        # 填写表单
        await page.fill('#name', '张三')
        await page.fill('#email', 'zhangsan@example.com')
        await page.fill('#age', '25')
        await page.select_option('#gender', 'male')
        await page.check('#agree')
        
        print("表单填写完成")
        
        # 获取表单数据进行验证
        name_value = await page.input_value('#name')
        email_value = await page.input_value('#email')
        age_value = await page.input_value('#age')
        gender_value = await page.input_value('#gender')
        is_checked = await page.is_checked('#agree')
        
        print(f"姓名: {name_value}")
        print(f"邮箱: {email_value}")
        print(f"年龄: {age_value}")
        print(f"性别: {gender_value}")
        print(f"同意条款: {is_checked}")
        
        await browser.close()
    print("✅ 表单处理示例完成\n")


async def screenshot_and_pdf_example():
    """截图和PDF生成示例"""
    print("📸 开始截图和PDF生成示例...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.goto("https://playwright.dev")
        
        # 截取整页截图
        await page.screenshot(path="playwright_homepage.png", full_page=True)
        print("已保存网页截图: playwright_homepage.png")
        
        # 截取特定元素
        hero_section = page.locator('.hero')
        if await hero_section.count() > 0:
            await hero_section.screenshot(path="hero_section.png")
            print("已保存Hero部分截图: hero_section.png")
        
        # 生成PDF（仅在Chromium中支持）
        await page.pdf(path="playwright_homepage.pdf", format="A4")
        print("已保存PDF文件: playwright_homepage.pdf")
        
        await browser.close()
    print("✅ 截图和PDF生成示例完成\n")


async def multi_page_example():
    """多页面操作示例"""
    print("🔄 开始多页面操作示例...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        # 创建多个页面
        page1 = await browser.new_page()
        page2 = await browser.new_page()
        
        # 并发访问不同网站
        await asyncio.gather(
            page1.goto("https://github.com"),
            page2.goto("https://stackoverflow.com")
        )
        
        # 获取两个页面的标题
        title1 = await page1.title()
        title2 = await page2.title()
        
        print(f"页面1标题: {title1}")
        print(f"页面2标题: {title2}")
        
        # 获取浏览器中所有页面
        all_pages = browser.contexts[0].pages
        print(f"当前打开的页面数量: {len(all_pages)}")
        
        await browser.close()
    print("✅ 多页面操作示例完成\n")


async def wait_and_error_handling_example():
    """等待和错误处理示例"""
    print("⏳ 开始等待和错误处理示例...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            # 设置页面超时时间
            page.set_default_timeout(5000)  # 5秒
            
            await page.goto("https://httpbin.org/delay/2")
            
            # 等待特定元素出现
            await page.wait_for_selector('pre', timeout=10000)
            print("页面加载成功，元素已出现")
            
            # 等待网络空闲
            await page.wait_for_load_state('networkidle')
            print("网络请求已完成")
            
        except Exception as e:
            print(f"发生错误: {str(e)}")
        
        await browser.close()
    print("✅ 等待和错误处理示例完成\n")


async def main():
    """主函数，运行所有示例"""
    print("🎭 Playwright 异步教学案例开始")
    print("=" * 50)
    
    examples = [
        basic_navigation_example,
        element_interaction_example,
        form_handling_example,
        screenshot_and_pdf_example,
        multi_page_example,
        wait_and_error_handling_example
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📖 示例 {i}: {example.__doc__.split()[0]}")
        try:
            await example()
        except Exception as e:
            print(f"❌ 示例 {i} 执行失败: {str(e)}")
        
        if i < len(examples):
            print("⏳ 等待3秒后继续下一个示例...")
            await asyncio.sleep(3)
    
    print("\n🎉 所有Playwright教学示例已完成！")
    print("\n💡 使用提示:")
    print("1. 确保已安装: pip install playwright")
    print("2. 安装浏览器: playwright install")
    print("3. 运行本脚本: python playwright_tutorial.py")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
