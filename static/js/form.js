document.addEventListener('DOMContentLoaded', function () {
    const contentArea = document.getElementById('content-area');
    const navButtons = document.querySelectorAll('.nav-btn');
    const prevButton = document.getElementById('prev-btn');
    const nextButton = document.getElementById('next-btn');
    const submitButton = document.getElementById('submit-btn');
    const statusMessage = document.getElementById('status-message');

    // 1. 定義頁面順序，與 form.html 中的按鈕 id 後綴對應
    const CATEGORIES = ['個人資料', '飲食篇', '生活篇', '心理篇'];
    let currentIndex = 0;

    // 渲染指定分類的內容
    async function renderContent(category) {
        const categoryIndex = CATEGORIES.indexOf(category);
        if (categoryIndex === -1) return;
        currentIndex = categoryIndex;

        // 更新導覽列按鈕的 active 狀態
        navButtons.forEach(btn => {
            btn.classList.toggle('active', btn.id === `nav-${category}`);
        });

        // 儲存目前頁面的答案
        saveAnswers();

        contentArea.innerHTML = '<p>正在載入...</p>';

        try {
            // 2. 統一所有分類的載入邏輯
            const response = await fetch(`/api/questions/${category}`);
            if (!response.ok) throw new Error('無法獲取問題');
            const categoryData = await response.json();

            let questionsHtml = `<h3>${categoryData.category}</h3><form id="health-form">`;
            categoryData.question.forEach((q, index) => {
                questionsHtml += `<div class="form-group"><label>${q.text}</label>`;
                // 處理需要輸入的欄位 (options 為空陣列)
                if (q.options.length === 0) {
                    questionsHtml += `<input type="text" name="${category}-q-${index}" class="text-input">`;
                } else { // 處理單選按鈕
                    q.options.forEach(optionText => {
                        const inputName = `${category}-q-${index}`;
                        const inputId = `${inputName}-${optionText.replace(/\s+/g, '-')}`;
                        questionsHtml += `
                            <span class="radio-option">
                                <input type="radio" name="${inputName}" id="${inputId}" value="${optionText}">
                                <label for="${inputId}">${optionText}</label>
                            </span>
                        `;
                    });
                }
                questionsHtml += `</div>`;
            });
            questionsHtml += `</form>`;
            contentArea.innerHTML = questionsHtml;

            restoreAnswers();
            updateActionButtons();

        } catch (error) {
            contentArea.innerHTML = `<p>內容載入失敗: ${error.message}</p>`;
        }
    }

    // 更新底部操作按鈕的顯示狀態
    function updateActionButtons() {
        prevButton.style.display = (currentIndex > 0) ? 'inline-block' : 'none';
        nextButton.style.display = (currentIndex < CATEGORIES.length - 1) ? 'inline-block' : 'none';
        submitButton.style.display = (currentIndex === CATEGORIES.length - 1) ? 'inline-block' : 'none';
    }

    // 儲存答案到 sessionStorage
    function saveAnswers() {
        const form = contentArea.querySelector('#health-form');
        if (!form) return;

        const formData = new FormData(form);
        let allAnswers = JSON.parse(sessionStorage.getItem('healthAnswers')) || {};

        // 1. 找出目前表單中所有的 input name
        const currentNames = Array.from(formData.keys());

        // 2. 在儲存新答案前，先從 allAnswers 中刪除所有與目前表單相關的舊答案
        //    這可以清除因程式碼變更而遺留的廢棄欄位
        for (const key in allAnswers) {
            // 檢查一個 key 是否屬於目前分類，例如 "飲食篇-q-0" 包含 "飲食篇"
            const categoryOfKey = key.split('-q-')[0];
            const currentCategory = CATEGORIES[currentIndex];
            if (categoryOfKey === currentCategory) {
                delete allAnswers[key];
            }
        }

        // 3. 將目前表單的新答案寫入
        for (const [name, value] of formData.entries()) {
            allAnswers[name] = value;
        }

        sessionStorage.setItem('healthAnswers', JSON.stringify(allAnswers));
    }

    // 從 sessionStorage 恢復答案
    function restoreAnswers() {
        const allAnswers = JSON.parse(sessionStorage.getItem('healthAnswers')) || {};
        for (const name in allAnswers) {
            const value = allAnswers[name];
            const inputs = document.getElementsByName(name);

            if (inputs.length > 0) {
                const inputType = inputs[0].type;

                if (inputType === 'radio') {
                    inputs.forEach(input => {
                        if (input.value === value) {
                            input.checked = true;
                        }
                    });
                } else { // 處理 text, number, select-one 等
                    inputs[0].value = value;
                }
            }
        }
    }

    // 為導覽列按鈕綁定事件
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const category = button.id.replace('nav-', '');
            renderContent(category);
        });
    });

    // 為新的底部按鈕綁定事件
    prevButton.addEventListener('click', () => {
        if (currentIndex > 0) {
            renderContent(CATEGORIES[currentIndex - 1]);
        }
    });

    nextButton.addEventListener('click', () => {
        if (currentIndex < CATEGORIES.length - 1) {
            renderContent(CATEGORIES[currentIndex + 1]);
        }
    });

    submitButton.addEventListener('click', async () => {
        saveAnswers(); // 儲存最後一頁的答案

        const allAnswers = JSON.parse(sessionStorage.getItem('healthAnswers')) || {};

        console.log('Final submission data:', allAnswers);
        statusMessage.innerText = '正在提交...';

        try {
            if (window.LIFF_ID) {
                await liff.init({ liffId: window.LIFF_ID });
                if (liff.isLoggedIn()) {
                    const profile = await liff.getProfile();
                    allAnswers.userId = profile.userId;
                }
            }
        } catch (e) { console.error("LIFF init failed", e); }

        try {
            const response = await fetch('/submit-form', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(allAnswers)
            });

            if (!response.ok) {
                const errorResult = await response.json();
                throw new Error(errorResult.message || '提交失敗');
            }

            const result = await response.json();
            statusMessage.innerText = result.message;
            sessionStorage.removeItem('healthAnswers');

            // 提交成功後可以選擇關閉 LIFF 視窗或顯示成功訊息
            alert('提交成功！');
            if (window.LIFF_ID && liff) {
                liff.closeWindow();
            }

        } catch (error) {
            statusMessage.innerText = `錯誤：${error.message}`;
        }
    });

    // 初始化：載入第一頁
    renderContent(CATEGORIES[0]);
});