const experimentsContainer = document.getElementById("experiments");
const inProgressTitle = document.getElementById("in-progress-title");
const completedTitle = document.getElementById("completed-title");
const buttonContainer = document.querySelector(".button-container");

function createExperimentElement(experimentInfo) {
    const experimentElement = document.createElement("div");
    experimentElement.className = "experiment";

    const checkboxElement = document.createElement("input");
    checkboxElement.setAttribute("type", "checkbox");
    checkboxElement.setAttribute("name", "experiment");
    checkboxElement.setAttribute("value", experimentInfo[0]);

    const labelElement = document.createElement("p");
    const statusElement = document.createElement("span");

    experimentElement.appendChild(checkboxElement);
    experimentElement.appendChild(labelElement);
    experimentElement.appendChild(statusElement);

    return experimentElement;
}

function isCompleted(status) {
    return status >= 3;
}

function createOrUpdateExperiment(experimentInfo) {
    const experimentID = experimentInfo[0];
    const experimentName = experimentInfo[1];
    const experimentStatus = experimentInfo[2];

    const inputElement = document.querySelector("input[type=\"checkbox\"][value=\"" + experimentID + "\"]");

    if(inputElement)
        var experimentElement = inputElement.parentElement;
    else
        var experimentElement = createExperimentElement(experimentInfo);
    
    const statusElement = experimentElement.querySelector("span");
    statusElement.className = "status status-" + experimentStatus;

    const labelElement = experimentElement.querySelector("p");
    labelElement.textContent = experimentName;

    if(isCompleted(experimentStatus)) {
        experimentsContainer.insertBefore(experimentElement, completedTitle.nextSibling);

        completedTitle.classList.remove("hidden");
        buttonContainer.classList.remove("hidden");

        experimentElement.querySelector("input").removeAttribute("disabled");
    }
    else {
        experimentsContainer.insertBefore(experimentElement, inProgressTitle.nextSibling);

        inProgressTitle.classList.remove("hidden");

        experimentElement.querySelector("input").setAttribute("disabled", "");
    }
}

function getExistingExperiments() {
    const checkboxElements = Array.from(document.querySelectorAll("input[name=experiment]"));

    return checkboxElements.reduce((accumulator, checkboxElement) => {
        accumulator[checkboxElement.value] = checkboxElement.parentElement;

        return accumulator;
    }, {});
}

async function updateAllExperiments() {
    const response = await fetch("/status").then((response) => response.json());
    const existingExperiments = getExistingExperiments();
     
    inProgressTitle.classList.add("hidden");
    completedTitle.classList.add("hidden");
    buttonContainer.classList.add("hidden");

    for(const experimentInfo of response) {
        createOrUpdateExperiment(experimentInfo);

        if(experimentInfo[0] in existingExperiments) {
            delete existingExperiments[experimentInfo[0]];
        }
    }

    for(const existingExperiment of Object.values(existingExperiments)) {
        existingExperiment.remove();
    }
}

function updateAllExperimentsRecursive(updateIntervalMilliseconds=2000) {
    updateAllExperiments();

    setTimeout(updateAllExperimentsRecursive, updateIntervalMilliseconds);
}

updateAllExperimentsRecursive();