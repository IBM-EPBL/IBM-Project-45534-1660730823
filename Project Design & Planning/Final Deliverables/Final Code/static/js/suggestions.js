let names = [
  "Java",
  "C",
  "Python",
  "C++",
  "C#",
  "HTML",
  "CSS",
  "JavaScript",
  "MySQL",
  "Figma",
  "XD",
  "Photoshop",
  "Azure Machine Learning",
  "T-SQL",
  "ASP.NET",
  "SQL Server",
  "MongoDB",
  "Angular",
  "Embededd C",
  "Visual Basic .NET",
  "AngularJS",
  "Spring Boot",
  "Fortran",
  "Node.js",
  "COBOL",
  "ReactJS",
  "jQuery",
  "TypeScript",
  "Jupyter",
  "Oracle",
  "Azure DevOps",
  "Software Developer",
  "Web Developer",
  "Data Scientist",
  ".NET Developer",
  "Senior Software Developer",
  "Embedded System Engineer",
  "Full Stack Developer",
  "UI/UX Designer",
  "Database Administrator",
  "Firmware Engineer",
  "Zoho Corporation",
  "Virtusa",
  "Aspire Systems",
  "DXC Tech",
  "VVDN",
  "Zuci Systems",
  "Hexaware Technologies",
  "Ami",
  "Mphasis",
  "TCS",
  "CTS",
  "RAPL Technology",
  "Wipro",
  "Hcl",
  "Lumen Tech",
  "HTC",
  "Infosys",
  "Accenture",
  "Quest",
  "Tech Mahindra",
  "Fujitsu",
  "Softsquare",
  "Adidhi",
  "CEI America ",
  "Link Logistics",
  "Atlassian",
  "Webberax",
  "Concentrix",
  "Embed UR Systems",
  "Pepul",
  "Info tech",
  "HData Systems",
  "IBM",
  "Microsoft",
  "Facebook",
  "Google",
  "Amazon",
  "Byjus",
  "Renault",
  "Oracle Cooperation",
  "Sales Force",
  "Adobe",
  "ServiceNow",
  "Deloitte",
  "Capgemini",
  "UST Global",
  "MIndTree",
  "Freshworks",
  "Cisco",
  "Cartoon MAngo",
  "GRL",
  "Apple"
];

let sortedNames = names.sort();
let input = document.getElementById("input");
input.addEventListener("keyup", (e) => {
  removeElements();
  for (let i of sortedNames) {
    if (
      i.toLowerCase().startsWith(input.value.toLowerCase()) &&
      input.value != ""
    ) {
      let listItem = document.createElement("li");
      listItem.classList.add("list-items");
      listItem.style.cursor = "pointer";
      listItem.setAttribute("onclick", "displayNames('" + i + "')");
      let word = "<b>" + i.substr(0, input.value.length) + "</b>";
      word += i.substr(input.value.length);
      listItem.innerHTML = word;
      document.querySelector(".list").appendChild(listItem);
    }
  }
});
function displayNames(value) {
  input.value = value;
  removeElements();
}
function removeElements() {
  let items = document.querySelectorAll(".list-items");
  items.forEach((item) => {
    item.remove();
  });
}