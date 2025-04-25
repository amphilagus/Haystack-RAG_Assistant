// upload_file.js
document.addEventListener('DOMContentLoaded', () => {
    /* ---------- 常用元素 ---------- */
    const dropZone      = document.querySelector('.drop-zone');
    const inputEl       = document.getElementById('files');
    const previewGrid   = document.getElementById('filePreview');
    const countBox      = document.getElementById('fileCount');
    const pdfCard       = document.getElementById('pdfOptionsCard');
    const uploadBtn     = document.getElementById('upload-btn');
    const uploadForm    = document.getElementById('upload-form');
  
    const progressModal = new bootstrap.Modal(document.getElementById('uploadProgressModal'));
    const progressBar   = document.getElementById('uploadProgressBar');
    const statusText    = document.getElementById('uploadStatusText');
  
    /* ---------- 工具函数 ---------- */
    const fmtSize = (b) => {
      if (!b) return '0 Bytes';
      const u = ['Bytes', 'KB', 'MB', 'GB'], k = 1024;
      const i = Math.floor(Math.log(b) / Math.log(k));
      return (b / Math.pow(k, i)).toFixed(2) + ' ' + u[i];
    };
  
    function fileIcon(ext) {
      const img = ['jpg','jpeg','png','gif','bmp','svg','webp'];
      const doc = ['doc','docx','odt','rtf'];
      const xls = ['xls','xlsx','csv'];
      const txt = ['txt','md']; const zip = ['zip','rar','7z','tar','gz'];
      const cod = ['js','html','css','py','java','c','cpp','rb','php'];
      if (ext === 'pdf')        return {i:'far fa-file-pdf',   c:'pdf'};
      if (img.includes(ext))    return {i:'far fa-file-image', c:'image'};
      if (doc.includes(ext))    return {i:'far fa-file-word',  c:'doc'};
      if (xls.includes(ext))    return {i:'far fa-file-excel', c:'excel'};
      if (txt.includes(ext))    return {i:'far fa-file-alt',   c:'text'};
      if (zip.includes(ext))    return {i:'far fa-file-archive',c:'archive'};
      if (cod.includes(ext))    return {i:'far fa-file-code',  c:'code'};
      return {i:'far fa-file',  c:''};
    }
  
    /* ---------- 预览与计数 ---------- */
    function updatePreview () {
      previewGrid.innerHTML = '';
      const files = Array.from(inputEl.files);
      if (!files.length){
        countBox.innerHTML = '';
        uploadBtn.disabled = true;
        pdfCard.style.display = 'none';
        return;
      }
  
      let total = 0, hasPDF=false;
      files.forEach((file, idx) => {
        total += file.size;
        if (file.name.toLowerCase().endsWith('.pdf')) hasPDF = true;
  
        const ext = file.name.split('.').pop().toLowerCase();
        const {i,c} = fileIcon(ext);
        const wrap  = document.createElement('div');
        wrap.className = 'file-item'; wrap.dataset.index = idx;
  
        wrap.innerHTML = `
          <div class="file-item__icon ${c}"><i class="${i}"></i></div>
          <div class="file-item__name">${file.name}</div>
          <div class="file-item__size">${fmtSize(file.size)}</div>
          <div class="file-item__remove" onclick="removeFile(${idx})">×</div>
        `;
        previewGrid.appendChild(wrap);
      });
  
      countBox.innerHTML = `
        <div><i class="fas fa-file me-1"></i> <span id="fileCounter">${files.length}</span> 个文件</div>
        <div><i class="fas fa-database me-1"></i> 总大小: ${fmtSize(total)}</div>
      `;
  
      uploadBtn.disabled = false;
      pdfCard.style.display = hasPDF ? 'block' : 'none';
    }
  
    /* ---------- 文件移除 ---------- */
    window.removeFile = function(idx) {
      const dt = new DataTransfer();
      const files = Array.from(inputEl.files);
      files.forEach((file, i) => {
        if (i !== idx) dt.items.add(file);
      });
      inputEl.files = dt.files;
      updatePreview();
    };
  
    /* ---------- 拖放功能 ---------- */
    dropZone.addEventListener('click', () => inputEl.click());
  
    // 阻止默认拖放行为
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, e => {
        e.preventDefault();
        e.stopPropagation();
      }, false);
      document.body.addEventListener(eventName, e => {
        e.preventDefault();
        e.stopPropagation();
      }, false);
    });
  
    // 拖放状态视觉反馈
    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.add('drop-zone--over');
      });
    });
  
    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('drop-zone--over');
      });
    });
  
    // 处理文件拖放
    dropZone.addEventListener('drop', e => {
      const dt = new DataTransfer();
      
      // 添加已有文件
      if (inputEl.files.length > 0) {
        Array.from(inputEl.files).forEach(file => dt.items.add(file));
      }
      
      // 添加新拖放的文件
      if (e.dataTransfer.files.length > 0) {
        Array.from(e.dataTransfer.files).forEach(file => dt.items.add(file));
      }
      
      inputEl.files = dt.files;
      updatePreview();
    });
  
    // 处理常规文件选择
    inputEl.addEventListener('change', updatePreview);
  
    /* ---------- 上传功能 ---------- */
    uploadBtn.addEventListener('click', async () => {
      if (!inputEl.files.length) return;
      
      // 准备表单数据
      const formData = new FormData(uploadForm);
      
      // 显示上传进度
      progressBar.style.width = '0%';
      statusText.textContent = '正在上传文件，请稍候...';
      progressModal.show();
      
      try {
        const response = await fetch(UPLOAD_ENDPOINT, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });
        
        const result = await response.json();
        
        if (result.success) {
          progressBar.style.width = '100%';
          statusText.textContent = '上传成功！正在重定向...';
          setTimeout(() => {
            window.location.href = result.task_id 
              ? `${TASKS_URL}/${result.task_id}`
              : TASKS_URL;
          }, 1000);
        } else {
          throw new Error(result.message || '上传失败');
        }
      } catch (error) {
        console.error('上传错误:', error);
        progressBar.classList.add('bg-danger');
        statusText.textContent = `上传失败: ${error.message}`;
        setTimeout(() => progressModal.hide(), 3000);
      }
    });
  
    /* ---------- 标签选择功能 ---------- */
    const tagCheckboxes = document.querySelectorAll('.tag-checkbox');
    const tagInput = document.getElementById('tags');
    const selectedTagsPreview = document.getElementById('selectedTagsPreview');
    const applyTagsBtn = document.getElementById('applyTags');
    const tagSearchInput = document.getElementById('tagSearchInput');
    
    // 更新选中标签预览
    function updateSelectedTags() {
      const selectedTags = [];
      tagCheckboxes.forEach(cb => {
        if (cb.checked) {
          selectedTags.push(cb.value);
        }
      });
      
      // 更新预览区域
      if (selectedTagsPreview) {
        if (selectedTags.length === 0) {
          selectedTagsPreview.innerHTML = '<span class="text-muted">未选择标签</span>';
        } else {
          selectedTagsPreview.innerHTML = selectedTags.map(tag => 
            `<span class="badge bg-primary me-1 mb-1">${tag}</span>`).join('');
        }
      }
      
      return selectedTags;
    }
    
    // 标签搜索功能
    if (tagSearchInput) {
      tagSearchInput.addEventListener('input', () => {
        const searchTerm = tagSearchInput.value.toLowerCase();
        document.querySelectorAll('.tag-item').forEach(item => {
          const tagName = item.textContent.toLowerCase();
          if (tagName.includes(searchTerm)) {
            item.style.display = '';
          } else {
            item.style.display = 'none';
          }
        });
      });
    }
    
    // 选择标签时更新预览
    tagCheckboxes.forEach(cb => {
      cb.addEventListener('change', updateSelectedTags);
    });
    
    // 应用选中的标签
    if (applyTagsBtn) {
      applyTagsBtn.addEventListener('click', () => {
        const selectedTags = updateSelectedTags();
        tagInput.value = selectedTags.join(', ');
        const tagModal = bootstrap.Modal.getInstance(document.getElementById('tagsModal'));
        tagModal.hide();
      });
    }
    
    // 初始化预览区域
    updateSelectedTags();
});
  