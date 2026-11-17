/**
 * TRUSTLENS — Client-side Interactive Behaviors & Forensics Workbench
 */

document.addEventListener("DOMContentLoaded", () => {
    initFileUploader();
    initInspectionTabs();
    initClipboard();
    initHistoryFilter();
    initHomePreviewToggle();
});

/* ==========================================================================
   1. File Uploader & Drag-and-Drop Viewfinder
   ========================================================================== */
function initFileUploader() {
    const fileInput = document.getElementById("receipt");
    const dropzone = document.getElementById("dropzone");
    const dropzoneContent = document.getElementById("dropzoneContent");
    const previewContainer = document.getElementById("previewContainer");
    const previewImg = document.getElementById("previewImg");
    const fileMetaStrip = document.getElementById("fileMetaStrip");
    const metaFileName = document.getElementById("metaFileName");
    const metaFileSize = document.getElementById("metaFileSize");
    const resetFileBtn = document.getElementById("resetFileBtn");
    const uploadForm = document.getElementById("uploadForm");
    const loadingScreen = document.getElementById("loadingScreen");

    if (!fileInput) return;

    // Handle Drag & Drop Events
    if (dropzone) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('drag-active');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('drag-active');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                fileInput.files = files;
                handleFileSelection(files[0]);
            }
        });
    }

    // Handle standard input change
    fileInput.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            handleFileSelection(this.files[0]);
        }
    });

    function handleFileSelection(file) {
        if (!file.type.match('image.*')) {
            alert('Please select a valid image receipt file (PNG, JPG, WEBP).');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            if (previewImg) previewImg.src = e.target.result;
            if (dropzoneContent) dropzoneContent.style.display = 'none';
            if (previewContainer) previewContainer.style.display = 'block';
            if (fileMetaStrip) fileMetaStrip.style.display = 'flex';

            if (metaFileName) metaFileName.textContent = file.name;
            if (metaFileSize) {
                const sizeKb = (file.size / 1024).toFixed(1);
                metaFileSize.textContent = sizeKb > 1024 
                    ? `${(sizeKb / 1024).toFixed(2)} MB` 
                    : `${sizeKb} KB`;
            }
        };
        reader.readAsDataURL(file);
    }

    // Reset button
    if (resetFileBtn) {
        resetFileBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            fileInput.value = '';
            if (previewImg) previewImg.src = '';
            if (dropzoneContent) dropzoneContent.style.display = 'flex';
            if (previewContainer) previewContainer.style.display = 'none';
            if (fileMetaStrip) fileMetaStrip.style.display = 'none';
        });
    }

    // Form submission & Stepwise Loading Animation
    if (uploadForm && loadingScreen) {
        uploadForm.addEventListener('submit', (e) => {
            if (!fileInput.files || fileInput.files.length === 0) {
                alert('Please select a receipt image before submitting.');
                e.preventDefault();
                return;
            }

            loadingScreen.style.display = 'flex';
            animateLoadingSteps();
        });
    }
}

function animateLoadingSteps() {
    const steps = [
        document.getElementById('stepTensor'),
        document.getElementById('stepMobileNet'),
        document.getElementById('stepEasyOCR'),
        document.getElementById('stepXGBoost'),
        document.getElementById('stepDossier')
    ];

    const validSteps = steps.filter(s => s !== null);
    if (validSteps.length === 0) return;

    let currentIndex = 0;
    validSteps[0].classList.add('active');

    const interval = setInterval(() => {
        if (currentIndex < validSteps.length - 1) {
            validSteps[currentIndex].classList.remove('active');
            validSteps[currentIndex].classList.add('done');
            const icon = validSteps[currentIndex].querySelector('i');
            if (icon) {
                icon.className = 'bi bi-check-circle-fill text-success';
            }

            currentIndex++;
            validSteps[currentIndex].classList.add('active');
            const nextIcon = validSteps[currentIndex].querySelector('i');
            if (nextIcon) {
                nextIcon.className = 'bi bi-arrow-repeat text-primary spinner-border spinner-border-sm';
            }
        } else {
            clearInterval(interval);
        }
    }, 1800);
}

/* ==========================================================================
   2. Result Page Inspection Tabs (Original / Heatmap / Side-by-Side)
   ========================================================================== */
function initInspectionTabs() {
    const tabBtns = document.querySelectorAll('.inspect-tab-btn');
    const viewOriginal = document.getElementById('viewOriginal');
    const viewHeatmap = document.getElementById('viewHeatmap');
    const viewDual = document.getElementById('viewDual');

    if (tabBtns.length === 0) return;

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const mode = btn.getAttribute('data-view');
            if (viewOriginal) viewOriginal.style.display = (mode === 'original') ? 'block' : 'none';
            if (viewHeatmap) viewHeatmap.style.display = (mode === 'heatmap') ? 'block' : 'none';
            if (viewDual) viewDual.style.display = (mode === 'dual') ? 'grid' : 'none';
        });
    });
}

/* ==========================================================================
   3. Clipboard Copy for UPI / Txn IDs
   ========================================================================== */
function initClipboard() {
    const copyBtns = document.querySelectorAll('.copy-btn');
    copyBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const textToCopy = btn.getAttribute('data-copy');
            if (!textToCopy) return;

            navigator.clipboard.writeText(textToCopy).then(() => {
                const origIcon = btn.innerHTML;
                btn.innerHTML = '<i class="bi bi-check2 text-success"></i>';
                setTimeout(() => {
                    btn.innerHTML = origIcon;
                }, 1800);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        });
    });
}

/* ==========================================================================
   4. History Table Live Filter & CSV Export
   ========================================================================== */
function initHistoryFilter() {
    const searchInput = document.getElementById('historySearch');
    const filterPills = document.querySelectorAll('.filter-pill');
    const tableRows = document.querySelectorAll('.custom-audit-table tbody tr');
    const exportCsvBtn = document.getElementById('exportCsvBtn');

    if (!searchInput && filterPills.length === 0) return;

    let activeFilter = 'all';

    function filterTable() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const statusAttr = row.getAttribute('data-status') || '';
            const riskAttr = row.getAttribute('data-risk') || '';

            const matchesQuery = query === '' || text.includes(query);
            let matchesFilter = true;

            if (activeFilter === 'real') {
                matchesFilter = statusAttr.toLowerCase() === 'real';
            } else if (activeFilter === 'fake') {
                matchesFilter = statusAttr.toLowerCase() === 'fake';
            } else if (activeFilter === 'high') {
                matchesFilter = riskAttr.toLowerCase() === 'high';
            }

            row.style.display = (matchesQuery && matchesFilter) ? '' : 'none';
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterTable);
    }

    filterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            filterPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            activeFilter = pill.getAttribute('data-filter') || 'all';
            filterTable();
        });
    });

    // CSV Export
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => {
            const csvRows = [[
                "ID", "Receipt", "Assessment", "Confidence", "Trust Score", "Risk Level", "Date"
            ]];

            tableRows.forEach(row => {
                if (row.style.display !== 'none') {
                    const cells = Array.from(row.querySelectorAll('td'))
                        .filter(cell => !cell.hasAttribute('data-csv-exclude'));
                    csvRows.push([
                        row.dataset.recordId || '',
                        ...cells.map(cell => cell.dataset.csvValue || '')
                    ]);
                }
            });

            const escapeCsvValue = value => `"${String(value).replace(/"/g, '""')}"`;
            const csvContent = csvRows
                .map(row => row.map(escapeCsvValue).join(','))
                .join('\r\n');
            const csvBlob = new Blob(['\uFEFF', csvContent], {
                type: 'text/csv;charset=utf-8'
            });
            const downloadUrl = URL.createObjectURL(csvBlob);
            const link = document.createElement("a");
            link.setAttribute("href", downloadUrl);
            link.setAttribute("download", `TrustLens_Audit_Log_${new Date().toISOString().slice(0, 10)}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 0);
        });
    }
}

/* ==========================================================================
   5. Interactive Hero Receipt Preview Toggle
   ========================================================================== */
function initHomePreviewToggle() {
    const toggleBtn = document.getElementById('heroToggleMode');
    const heroScanView = document.getElementById('heroScanView');
    const heroNormalView = document.getElementById('heroNormalView');

    if (!toggleBtn || !heroScanView) return;

    toggleBtn.addEventListener('click', () => {
        const isScanActive = heroScanView.style.display !== 'none';
        if (isScanActive) {
            heroScanView.style.display = 'none';
            if (heroNormalView) heroNormalView.style.display = 'block';
            toggleBtn.innerHTML = '<i class="bi bi-eye"></i> Show Neural Scan';
        } else {
            heroScanView.style.display = 'flex';
            if (heroNormalView) heroNormalView.style.display = 'none';
            toggleBtn.innerHTML = '<i class="bi bi-shield-check"></i> Standard View';
        }
    });
}
