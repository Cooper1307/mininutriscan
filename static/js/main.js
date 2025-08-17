// 主要的JavaScript功能
class NutriScanApp {
    constructor() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.previewContainer = document.getElementById('previewContainer');
        this.previewImage = document.getElementById('previewImage');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.loadingDiv = document.getElementById('loading');
        this.resultsDiv = document.getElementById('results');
        this.nutritionInfo = document.getElementById('nutritionInfo');
        this.healthAdvice = document.getElementById('healthAdvice');
        
        this.initEventListeners();
    }

    initEventListeners() {
        // 文件上传区域事件
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });

        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        // 分析按钮事件
        this.analyzeBtn.addEventListener('click', () => {
            this.analyzeImage();
        });

        // 用户信息表单事件
        const userForm = document.getElementById('userForm');
        if (userForm) {
            userForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveUserProfile();
            });
        }
    }

    handleFileSelect(file) {
        // 验证文件类型
        if (!file.type.startsWith('image/')) {
            this.showAlert('请选择图片文件！', 'danger');
            return;
        }

        // 验证文件大小（5MB限制）
        if (file.size > 5 * 1024 * 1024) {
            this.showAlert('图片文件大小不能超过5MB！', 'danger');
            return;
        }

        // 显示预览
        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImage.src = e.target.result;
            this.previewContainer.style.display = 'block';
            this.analyzeBtn.disabled = false;
            this.uploadArea.style.display = 'none';
            
            // 添加淡入动画
            this.previewContainer.classList.add('fade-in');
        };
        reader.readAsDataURL(file);

        // 存储文件引用
        this.selectedFile = file;
    }

    async analyzeImage() {
        if (!this.selectedFile) {
            this.showAlert('请先选择图片！', 'warning');
            return;
        }

        // 显示加载状态
        this.showLoading(true);
        this.analyzeBtn.disabled = true;

        try {
            // 创建FormData
            const formData = new FormData();
            formData.append('image', this.selectedFile);

            // 获取用户信息
            const userProfile = this.getUserProfile();
            if (userProfile) {
                Object.keys(userProfile).forEach(key => {
                    formData.append(key, userProfile[key]);
                });
            }

            // 发送请求
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.displayResults(result.data);
            } else {
                throw new Error(result.error || '分析失败');
            }

        } catch (error) {
            console.error('分析错误:', error);
            this.showAlert(`分析失败: ${error.message}`, 'danger');
        } finally {
            this.showLoading(false);
            this.analyzeBtn.disabled = false;
        }
    }

    displayResults(data) {
        // 显示营养信息
        if (data.nutrition) {
            this.nutritionInfo.innerHTML = this.formatNutritionInfo(data.nutrition);
        }

        // 显示健康建议
        if (data.advice) {
            this.healthAdvice.innerHTML = this.formatHealthAdvice(data.advice);
        }

        // 显示结果区域
        this.resultsDiv.style.display = 'block';
        this.resultsDiv.classList.add('fade-in');

        // 滚动到结果区域
        this.resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    formatNutritionInfo(nutrition) {
        let html = '<div class="row">';
        
        const nutritionItems = [
            { key: 'calories', label: '卡路里', unit: 'kcal', icon: '🔥' },
            { key: 'protein', label: '蛋白质', unit: 'g', icon: '💪' },
            { key: 'carbs', label: '碳水化合物', unit: 'g', icon: '🌾' },
            { key: 'fat', label: '脂肪', unit: 'g', icon: '🥑' },
            { key: 'fiber', label: '纤维', unit: 'g', icon: '🌿' },
            { key: 'sugar', label: '糖分', unit: 'g', icon: '🍯' }
        ];

        nutritionItems.forEach(item => {
            const value = nutrition[item.key] || 0;
            html += `
                <div class="col-md-4 col-sm-6 mb-3">
                    <div class="nutrition-item text-center">
                        <div class="nutrition-icon" style="font-size: 2rem; margin-bottom: 10px;">${item.icon}</div>
                        <div class="nutrition-value">${value}${item.unit}</div>
                        <div class="nutrition-label">${item.label}</div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        return html;
    }

    formatHealthAdvice(advice) {
        let html = '<div class="advice-content">';
        
        if (advice.summary) {
            html += `<p class="lead mb-4">${advice.summary}</p>`;
        }
        
        if (advice.recommendations && advice.recommendations.length > 0) {
            html += '<h5 class="mb-3">💡 个性化建议</h5><ul class="list-unstyled">';
            advice.recommendations.forEach(rec => {
                html += `<li class="mb-2">✅ ${rec}</li>`;
            });
            html += '</ul>';
        }
        
        if (advice.warnings && advice.warnings.length > 0) {
            html += '<h5 class="mb-3 mt-4">⚠️ 注意事项</h5><ul class="list-unstyled">';
            advice.warnings.forEach(warning => {
                html += `<li class="mb-2">⚠️ ${warning}</li>`;
            });
            html += '</ul>';
        }
        
        html += '</div>';
        return html;
    }

    getUserProfile() {
        const form = document.getElementById('userForm');
        if (!form) return null;

        const formData = new FormData(form);
        const profile = {};
        
        for (let [key, value] of formData.entries()) {
            profile[key] = value;
        }
        
        return profile;
    }

    saveUserProfile() {
        const profile = this.getUserProfile();
        if (profile) {
            localStorage.setItem('userProfile', JSON.stringify(profile));
            this.showAlert('用户信息已保存！', 'success');
        }
    }

    loadUserProfile() {
        const saved = localStorage.getItem('userProfile');
        if (saved) {
            try {
                const profile = JSON.parse(saved);
                const form = document.getElementById('userForm');
                if (form) {
                    Object.keys(profile).forEach(key => {
                        const input = form.querySelector(`[name="${key}"]`);
                        if (input) {
                            input.value = profile[key];
                        }
                    });
                }
            } catch (error) {
                console.error('加载用户信息失败:', error);
            }
        }
    }

    showLoading(show) {
        if (show) {
            this.loadingDiv.style.display = 'block';
            this.loadingDiv.classList.add('fade-in');
        } else {
            this.loadingDiv.style.display = 'none';
        }
    }

    showAlert(message, type = 'info') {
        // 移除现有的alert
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }

        // 创建新的alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // 插入到页面顶部
        const container = document.querySelector('.container');
        container.insertBefore(alert, container.firstChild);

        // 自动消失
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    resetUpload() {
        this.selectedFile = null;
        this.previewContainer.style.display = 'none';
        this.uploadArea.style.display = 'block';
        this.resultsDiv.style.display = 'none';
        this.analyzeBtn.disabled = true;
        this.fileInput.value = '';
    }
}

// 工具函数
function formatNumber(num, decimals = 1) {
    return parseFloat(num).toFixed(decimals);
}

function calculateBMI(weight, height) {
    const heightInMeters = height / 100;
    return weight / (heightInMeters * heightInMeters);
}

function getBMICategory(bmi) {
    if (bmi < 18.5) return '偏瘦';
    if (bmi < 24) return '正常';
    if (bmi < 28) return '超重';
    return '肥胖';
}

function getRecommendedCalories(weight, height, age, gender, activity) {
    // 基础代谢率计算（Harris-Benedict公式）
    let bmr;
    if (gender === 'male') {
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
    } else {
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
    }
    
    // 活动系数
    const activityFactors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    };
    
    return bmr * (activityFactors[activity] || 1.2);
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', function() {
    const app = new NutriScanApp();
    
    // 加载保存的用户信息
    app.loadUserProfile();
    
    // 添加重置按钮功能
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            app.resetUpload();
        });
    }
    
    // 添加工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 添加平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// 导出给全局使用
window.NutriScanApp = NutriScanApp;