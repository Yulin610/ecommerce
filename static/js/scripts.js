// 鼠标悬停事件
document.querySelectorAll("nav a").forEach(function (anchor) {
    anchor.addEventListener("mouseover", function () {
        var position = anchor.getBoundingClientRect();  // 获取元素相对于视口的位置
        var width = anchor.offsetWidth;  // 获取元素的宽度
        var height = anchor.offsetHeight;  // 获取元素的高度

        console.log("Mouseover event - position:", position, "width:", width, "height:", height);

        var slide2 = document.querySelector("nav .slide2");
        if (slide2) { // 确保 slide2 元素存在
            var navOffset = document.querySelector("nav").offsetLeft;

            slide2.style.opacity = 1;
            slide2.style.visibility = 'visible';  // 确保可见
            slide2.style.left = position.left - navOffset + 'px';  // 计算相对于 nav 的位置
            slide2.style.top = position.top + height - document.querySelector("nav").offsetTop + 'px'; // 让 slide2 位于菜单项下方
            slide2.style.width = width + 'px';
            slide2.classList.add("squeeze");
        }
    });

    // 点击事件
    anchor.addEventListener("click", function () {
        var position = anchor.getBoundingClientRect();
        var width = anchor.offsetWidth;
        var height = anchor.offsetHeight;

        console.log("Click event - position:", position, "width:", width, "height:", height);

        var slide1 = document.querySelector("nav .slide1");
        if (slide1) { // 确保 slide1 元素存在
            slide1.style.opacity = 1;
            slide1.style.visibility = 'visible';  // 确保可见
            slide1.style.left = position.left + 'px';
            slide1.style.top = position.top + height + 'px';
            slide1.style.width = width + 'px';
        }
    });

    // 鼠标移出事件
    anchor.addEventListener("mouseout", function () {
        console.log("Mouseout event triggered");
        var slide2 = document.querySelector("nav .slide2");
        if (slide2) { // 确保 slide2 元素存在
            slide2.style.opacity = 0;
            slide2.style.visibility = 'hidden';  // 隐藏透明框并避免它阻止点击
            slide2.classList.remove("squeeze");
        }
    });
});

// 验证表单
function validateForm(event) {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // 检查用户名和密码长度
    if (username.length < 3 || username.length > 13 || password.length < 3 || password.length > 13) {
        alert('Username and password must be between 3 and 13 characters!');
        event.preventDefault(); // 阻止表单提交
        return false;
    }

    // 进行邮箱验证
    return validateEmail(event);
}

// 幻灯片切换
let chosenSlideNumber = 1;
let offset = 0;
let barOffset = 0;
let intervalID;

// 启动幻灯片轮播
startSlide();

// 获取所有抽屉按钮，并为每个按钮添加点击事件监听器
document.querySelectorAll(".drawer-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
        clearInterval(intervalID); // 清除定时器
        startSlide(); // 重新启动幻灯片轮播
    });
});

// 获取幻灯片区域
const slideSection = document.querySelector("#slide-section");
if (slideSection) {
    // 鼠标移入幻灯片区域时清除定时器
    slideSection.addEventListener("mouseenter", function () {
        clearInterval(intervalID);
    });

    // 鼠标移出幻灯片区域时重新启动幻灯片轮播
    slideSection.addEventListener("mouseleave", function () {
        startSlide();
    });
}

// 切换到指定编号的幻灯片
function slideTo(slideNumber) {
    drawerboxToggle(slideNumber); // 切换抽屉面板状态
    drawerbtnToggle(slideNumber); // 切换抽屉按钮状态

    let previousSlideNumber = chosenSlideNumber;
    chosenSlideNumber = slideNumber;
    offset += (chosenSlideNumber - previousSlideNumber) * (-100); // 计算幻灯片偏移量
    barOffset += (chosenSlideNumber - previousSlideNumber) * (100); // 计算导航条偏移量
    barSlide(barOffset); // 移动导航条

    // 获取所有幻灯片，为每个幻灯片设置偏移量
    document.querySelectorAll(".card").forEach(function (slide) {
        slide.style.transform = `translateY(${offset}%)`;
    });
}

// 切换抽屉面板状态
function drawerboxToggle(drawerboxNumber) {
    let prevDrawerboxNumber = chosenSlideNumber;
    const drawerboxes = document.querySelectorAll(".drawerbox");

    if (drawerboxes.length > 0) {
        // 确保 drawerboxes 数组有元素
        drawerboxes[prevDrawerboxNumber - 1]?.classList.toggle("active");
        drawerboxes[drawerboxNumber - 1]?.classList.toggle("active");
    } else {
        console.warn("No drawerbox elements found.");
    }
}

// 切换抽屉按钮状态
function drawerbtnToggle(drawerBtnNumber) {
    let prevDrawerBtnNumber = chosenSlideNumber;
    const drawerBtns = document.querySelectorAll(".drawer-btn");

    if (drawerBtns.length > 0) {
        drawerBtns[prevDrawerBtnNumber - 1]?.classList.toggle("active"); // 切换前一个抽屉按钮的状态
        drawerBtns[drawerBtnNumber - 1]?.classList.toggle("active"); // 切换当前抽屉按钮的状态
    } else {
        console.warn("No drawer button elements found.");
    }
}

// 移动导航条
function barSlide(barOffset) {
    const bar = document.querySelector("#bar");
    if (bar) { // 确保 bar 元素存在
        bar.style.transform = `translateY(${barOffset}%)`;
    } else {
        console.warn("No bar element found.");
    }
}

// 启动幻灯片轮播
function startSlide() {
    intervalID = setInterval(function () {
        slideTo(chosenSlideNumber % 4 + 1); // 每次切换到下一个幻灯片
    }, 3000); // 每隔 3 秒自动切换幻灯片
}

document.querySelectorAll(".like-unlike-btn").forEach(button => {
    button.addEventListener("click", function (event) {
        console.log("Like button clicked");

        const target = event.target;
        const productId = target.dataset.productId;

        if (!productId) {
            console.error("Product ID is missing!");
            return;
        }

        console.log("Product ID: " + productId);

        const csrfToken = document.getElementById('csrf_token').value; // 获取页面上的 CSRF Token
        console.log("CSRF Token: ", csrfToken);  // 打印 CSRF Token

        let url, method;
        if (target.textContent.trim() === "Like") {
            url = "/like_product/" + productId;
            method = "GET";
        } else if (target.textContent.trim() === "Unlike") {
            url = "/unlike_product/" + productId;
            method = "GET";
        }

        // 发出 fetch 请求
        fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",  // 设置为 JSON 格式
                "X-CSRFToken": csrfToken  // 发送 CSRF Token
            },
            //body: JSON.stringify({ product_id: productId }) // 使用 JSON 格式传递数据
        })
        .then(response => {
            console.log("Response status: ", response.status);
            return response.json(); // 确保解析为 JSON
        })
        .then(data => {
            console.log(data);
            if (data.success) {
                if (target.textContent.trim() === "Like") {
                    target.textContent = "Unlike";
                } else {
                    target.textContent = "Like";
                }

            } else {
                alert(data.message);
            }
            // 获取当前页面的路径部分
            const currentPath = window.location.pathname;

            // 检查路径是否为 '/profile'
            if (currentPath === '/profile') {
            // 刷新页面
                location.reload();
            }

        })
        .catch(error => {
            console.error(error);
            alert("Error liking/unliking the product.");
        });
    });
});


