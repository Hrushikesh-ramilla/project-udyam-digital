import os
import time
import math
from playwright.sync_api import sync_playwright, Page

def inject_cursor(page: Page):
    cursor_js = """
    (() => {
        if (document.getElementById('playwright-mouse-pointer')) return;
        const cursor = document.createElement('div');
        cursor.id = 'playwright-mouse-pointer';
        cursor.style.width = '20px';
        cursor.style.height = '20px';
        cursor.style.borderRadius = '50%';
        cursor.style.position = 'fixed';
        cursor.style.left = '960px';
        cursor.style.top = '540px';
        cursor.style.zIndex = '999999';
        cursor.style.pointerEvents = 'none';
        cursor.style.backgroundColor = 'rgba(228, 0, 0, 0.5)';
        cursor.style.border = '2px solid #ffffff';
        cursor.style.boxShadow = '0 0 12px rgba(228, 0, 0, 0.9), 0 0 4px rgba(255, 255, 255, 0.8)';
        cursor.style.transition = 'transform 0.08s ease-out, background-color 0.15s ease';
        cursor.style.transform = 'translate(-50%, -50%)';
        document.body.appendChild(cursor);
        
        window.addEventListener('mousemove', e => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });
        window.addEventListener('mousedown', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(0.65)';
            cursor.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        });
        window.addEventListener('mouseup', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(1)';
            cursor.style.backgroundColor = 'rgba(228, 0, 0, 0.5)';
        });
    })();
    """
    page.evaluate(cursor_js)

def smooth_move(page: Page, target_x: float, target_y: float, steps: int = 25, delay_ms: float = 12):
    # Get current pos from evaluation
    curr = page.evaluate("() => { const c = document.getElementById('playwright-mouse-pointer'); return c ? {x: parseFloat(c.style.left), y: parseFloat(c.style.top)} : {x: 960, y: 540}; }")
    start_x, start_y = curr["x"], curr["y"]
    
    for i in range(1, steps + 1):
        t = i / steps
        # smooth ease-in-out
        ease = 0.5 - 0.5 * math.cos(t * math.pi)
        cur_x = start_x + (target_x - start_x) * ease
        cur_y = start_y + (target_y - start_y) * ease
        page.mouse.move(cur_x, cur_y)
        time.sleep(delay_ms / 1000.0)

def human_click(page: Page, locator, steps: int = 20):
    box = locator.bounding_box()
    if box:
        tx = box["x"] + box["width"] / 2
        ty = box["y"] + box["height"] / 2
        smooth_move(page, tx, ty, steps=steps)
        time.sleep(0.15)
        page.mouse.click(tx, ty)
        time.sleep(0.2)

def human_type(page: Page, locator, text: str, min_delay: float = 0.025, max_delay: float = 0.055):
    human_click(page, locator)
    import random
    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(min_delay, max_delay))
