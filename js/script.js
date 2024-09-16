// ========================================================================== //
//                              global variables                              //
// ========================================================================== //
let config;
let currentFile;
let debouncedHandleHover;
let breadcrumbs = [];


// function escapeHtml(unsafe) {
//     return unsafe
//         .replace(/&/g, "&amp;")
//         .replace(/</g, "&lt;")
//         .replace(/>/g, "&gt;")
//         .replace(/"/g, "&quot;")
//         .replace(/'/g, "&#039;");
// }


// ========================================================================== //
//                             Load & Inject HTML                             //
// ========================================================================== //
function displayContentFromHtml(filePath, panelId) {
    // Get the panel element
    const panel = document.getElementById(panelId);

    // Show loading indicator
    panel.innerHTML = '<div class="loading">Loading...</div>';

    // Return a promise that resolves with the parsed JSON
    return fetch(filePath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            // Set the panel's content to the loaded HTML
            panel.innerHTML = html;

            // Parse the page data
            const pageDataScript = panel.querySelector('script[type="application/json"]#page-data');
            if (pageDataScript) {
                return JSON.parse(pageDataScript.textContent);
            } else {
                console.warn('No page data found in the loaded content');
                return null;
            }
        })
        .catch(error => {
            console.error('Error loading content:', error);
            
            // Display error message in the panel
            panel.innerHTML = `
                <div class="error-message">
                    <h3>Error Loading Content</h3>
                    <p>${error.message}</p>
                    <p>File: ${filePath}</p>
                </div>
            `;

            // Re-throw the error to be caught by the caller
            throw error;
        });
}


// ========================================================================== //
//                           Intialization functions                          //
// ========================================================================== //
function initializeConfig() {
    console.log(`INFO : initializeConfig()`);
    return parseYamlFile('config.yaml')
        .then(parsedConfig => {
            config = parsedConfig;
            currentFile = config.display.pathData + config.display.initFile;
            console.log(`      currentFile = '%s'`, currentFile);

            // Initialize debouncedHandleHover here, after config is loaded
            debouncedHandleHover = debounce(handleHover, config.display.debounceTime);
        })
        .catch(error => {
            console.error('Failed to initialize config:', error);
            throw error;
        });
}


function initializeBreadcrumbs() {
    console.log(`INFO : initializeBreadcrumbs()`);
    let fullFilePath = config.display.pathData + config.display.initFile
    displayContentFromHtml(fullFilePath, 'navigator-panel-left')
        .then(pageData => {
            if (pageData) {
                console.log('Page Title:', pageData.pageTitle);
                breadcrumbs = [{ title: pageData.pageTitle, filePath: fullFilePath }];
                console.log(`      breadcrumbs[0].title = '%s'`, breadcrumbs[0].title);
                console.log(`      breadcrumbs[0].filePath = '%s'`, breadcrumbs[0].filePath);
                displayBreadcrumbs();
            } else {
                console.log('No page data available');
                breadcrumbs = [{ title: "NONE", filePath: fullFilePath }];
                console.log(`      breadcrumbs[0].title = '%s'`, breadcrumbs[0].title);
                console.log(`      breadcrumbs[0].filePath = '%s'`, breadcrumbs[0].filePath);
                displayBreadcrumbs();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}



// ========================================================================== //
//                                Intialization                               //
// ========================================================================== //
initializeConfig()
  .then(() => {
    initializeBreadcrumbs();
    scheduleHeapLogging();
  })
  .catch(error => {
    console.error('Initialization failed:', error);
  });

// ========================================================================== //
//                                DEBUG                               //
// ========================================================================== //

function logHeapUsage() {
    if (window.performance) {
        if (window.performance.memory) {
            // Chrome, Edge
            const memory = window.performance.memory;
            console.log(`Total JS heap size: ${memory.totalJSHeapSize / 1048576} MB`);
            console.log(`Used JS heap size: ${memory.usedJSHeapSize / 1048576} MB`);
        } else if (window.performance.getEntriesByType) {
            // Firefox and other browsers
            const memory = window.performance.getEntriesByType('memory');
            if (memory.length > 0) {
                console.log(`JS heap size: ${memory[0].jsHeapSizeLimit / 1048576} MB`);
                console.log(`Used JS heap size: ${memory[0].usedJSHeapSize / 1048576} MB`);
            } else {
                console.log('Memory information not available');
            }
        } else {
            console.log('Memory performance API not supported in this browser');
        }
    } else {
        console.log('Performance API not supported in this browser');
    }
}

function scheduleHeapLogging() {
    logHeapUsage();
    setTimeout(scheduleHeapLogging, config.performance.loggingTime);
}

// ========================================================================== //
//                                YAML functions                              //
// ========================================================================== //
function parseYamlFile(filePath) {
    console.log(`INFO : parseYamlFile(filePath='%s')`, filePath);
    return fetch(filePath)
        .then(response => response.text())
        .then(yamlText => jsyaml.load(yamlText))
        .catch(error => {
            console.error('Error loading YAML file:', error);
            throw error;
        });
}


// ========================================================================== //
//                              Utility functions                             //
// ========================================================================== //
function resolvePath(...parts) {
    let base = new URL('http://example.com/');

    for (let part of parts) {
        part = part.replace(/^\/|\/$/g, '');
        if (!part) continue;
        base = new URL(part, base);
    }
    let result = base.pathname.replace(/^\//, '');
    return '/' + result;
}


function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}


// ========================================================================== //
//                            Interactive functions                           //
// ========================================================================== //
function handleClick(title, filePath) {
    console.log(`INFO : handleClick(title='%s' , filePath='%s')`, title, filePath);
    currentFile = config.display.pathData + filePath;
    displayContentFromHtml(currentFile, 'navigator-panel-left')
        .then(pageData => {
            if (pageData) {
                console.log('Page Title:', pageData.pageTitle);
                // Use other data from pageData as needed
                updateBreadcrumbs(pageData.pageTitle, currentFile);
            } else {
                console.log('No page data available');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    clearRightPanel();
}


function handleHover(filePath) {
    console.log(`INFO : handleHover(filePath='%s/%s')`, config.display.pathData, filePath);
    let fullFilePath = config.display.pathData + filePath
    displayContentFromHtml(fullFilePath, 'navigator-panel-right');
}


function clearRightPanel() {
    console.log(`INFO : clearRightPanel()`);
    document.getElementById('navigator-panel-right').innerHTML = '';
}


// ========================================================================== //
//                                 Breadcrumbs                                //
// ========================================================================== //
function updateBreadcrumbs(title, filePath) {
    console.log(`INFO : updateBreadcrumbs(title='%s' , filePath='%s')`, title, filePath);
    const existingIndex = breadcrumbs.findIndex(item => item.filePath === filePath);
    if (existingIndex !== -1) {
        breadcrumbs = breadcrumbs.slice(0, existingIndex + 1);
    } else {
        breadcrumbs.push({ title: title, filePath: config.display.pathData + filePath });
    }
    
    displayBreadcrumbs();
}


function displayBreadcrumbs() {
    console.log('INFO : displayBreadcrumbs()');
    let breadcrumbString = '';
    for (let i = 0; i < breadcrumbs.length; i++) {
        let crumb = breadcrumbs[i];
        breadcrumbString += `'${crumb.title}' [${crumb.filePath}]`;
        
        // Add the arrow if it's not the last item
        if (i < breadcrumbs.length - 1) {
            breadcrumbString += ' -> ';
        }
    }
    console.log('      breadcrumbs: ', breadcrumbString);

    const breadcrumbsElement = document.getElementById('navigator-breadcrumbs');
    breadcrumbsElement.innerHTML = breadcrumbs.map((item, index) => {
        if (index === breadcrumbs.length - 1) {
            return `<span>${item.title}</span>`;
        }
        return `<a href="#" onclick="handleBreadcrumbClick('${item.filePath}', ${index})">${item.title}</a> > `;
    }).join('');
}


function handleBreadcrumbClick(filePath, index) {
    console.log(`INFO : displayBreadcrumbs(filePath='%s/%s' , index='%s')`, config.display.pathData, filePath, index);
    breadcrumbs = breadcrumbs.slice(0, index + 1);
    displayBreadcrumbs();
    displayContentFromHtml(filePath, 'navigator-panel-left');
}



