# Agile Reporting System

A comprehensive full-stack application for Agile development methodology with advanced reporting features, team management, and complete project health tracking. Built with Spring Boot and React.

## 🎯 Overview

This system provides a complete Agile project management solution with:
- **Comprehensive Project Health Tracking** - All standard Agile metrics
- **Team Velocity Monitoring** - Track and forecast team performance
- **Defect & Quality Management** - Complete defect lifecycle tracking
- **Sprint Goal Achievement** - Track sprint success rates
- **Customizable Reporting** - Flexible report generation and export

## ✨ Key Features

### Project Management
- Create and manage multiple Agile projects
- Track project status (Planning, Active, On Hold, Completed, Cancelled)
- Monitor health status (Healthy, At Risk, Critical)
- Document risk indicators
- Team size tracking

### Team Management
- Add team members with Agile roles (Product Owner, Scrum Master, Developer, Tester, Stakeholder)
- Assign members to specific projects
- Track active/inactive status
- Role-based team statistics

### Sprint Management
- Create and manage sprints with dates and story points
- Set sprint goals and track achievement
- Record stakeholder feedback from Sprint Reviews
- Track sprint status (Planned, Active, Completed, Cancelled)
- Calculate velocity automatically

### Task Management
- Create tasks with multiple types:
  - **Story** - User stories
  - **Bug** - Software bugs
  - **Defect** - Quality issues
  - **Task** - General work items
  - **Technical Debt** - Code quality improvements
  - **Spike** - Research/investigation
- Track status (To Do, In Progress, In Review, Done, Blocked)
- Set priority (Low, Medium, High, Critical)
- Assign story points
- Assign to team members

### Defect Tracking System
- Complete defect lifecycle management
- Track severity (Trivial, Minor, Major, Critical, Blocker)
- Monitor status (New, Open, In Progress, Resolved, Closed, Reopened)
- Set priority (Low, Medium, High, Urgent)
- Mark escaped defects (production bugs)
- Record root cause analysis
- Assign to team members
- Track found date and resolved date

### Comprehensive Health Reports Dashboard

The Enhanced Health Reports page provides ALL standard Agile metrics in one place:

#### 1. **Burndown Chart** 📉
- Tracks remaining work vs. time for sprints
- Shows planned vs completed vs remaining story points
- Visual bar chart representation

#### 2. **Burn-up Chart** 📈
- Tracks completed work vs. total scope
- Useful when scope changes during project
- Line chart showing cumulative progress

#### 3. **Cumulative Flow Diagram (CFD)** 🌊
- Shows flow of work through Kanban states
- Visualizes To Do → In Progress → Done
- Stacked area chart for work distribution

#### 4. **Definition of Done (DoD) Adherence** ✅
- Percentage showing quality and completeness
- Ensures work meets acceptance criteria
- Calculated from completed vs planned story points

#### 5. **Sprint Goal Achievement** 🎯
- Tracks whether sprint goals were met
- Success rate across completed sprints
- Percentage metric display

#### 6. **Defect Trends / Quality Metrics** 🐛
- Tracks open defects, resolved defects, escaped defects
- Shows defect density over time
- Bar chart visualization

#### 7. **Stakeholder Feedback** 💬
- Qualitative measure from Sprint Reviews
- Captures perceived project progress
- Text feedback display

#### 8. **Risk Indicators** ⚠️
- Project-specific risks and concerns
- Highlighted warning section
- Proactive risk management

### Velocity Reports
- Track story points completed per sprint
- Calculate average velocity (3-5 sprint rolling average)
- Compare planned vs actual velocity
- Visualize velocity trends with charts
- Forecast future capacity

### Custom Report Builder
- **Flexible Metrics Selection**: Choose which metrics to include
- **Multiple Chart Types**: Bar charts, line charts, pie charts
- **Data Grouping Options**: Group by sprint or task status
- **Date Range Filtering**: All-time, last 3/6 sprints, current sprint
- **Report Types**: Summary, detailed, or trend analysis
- **Export Functionality**: Export as JSON or Text format
- **PDF Generation**: Generate PDF reports

## 🛠 Technology Stack

### Backend
- **Spring Boot 3.2.0** - Java-based backend framework
- **Spring Data JPA** - Database access and ORM
- **H2 Database** - In-memory database (auto-schema generation)
- **Maven** - Build and dependency management
- **Lombok** - Reduce boilerplate code
- **iText PDF** - PDF report generation

### Frontend
- **React 18** - Modern UI library
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Recharts** - Data visualization and charts
- **CSS3** - Responsive styling

## 📁 Project Structure

```
Agile/
├── backend/                          # Spring Boot Backend
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/agile/
│   │   │   │   ├── model/           # Entity classes
│   │   │   │   │   ├── Project.java
│   │   │   │   │   ├── Sprint.java (enhanced)
│   │   │   │   │   ├── Task.java (enhanced)
│   │   │   │   │   ├── Defect.java (new)
│   │   │   │   │   ├── ProjectMember.java
│   │   │   │   │   └── ...
│   │   │   │   ├── repository/      # JPA repositories
│   │   │   │   ├── service/         # Business logic
│   │   │   │   ├── controller/      # REST controllers
│   │   │   │   ├── dto/             # Data transfer objects
│   │   │   │   └── config/          # Configuration
│   │   │   └── resources/
│   │   │       └── application.properties
│   │   └── pom.xml
│   └──
├── frontend/                         # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.js
│   │   │   ├── ProjectList.js
│   │   │   ├── TeamManagement.js
│   │   │   ├── SprintManagement.js
│   │   │   ├── EnhancedHealthReport.js
│   │   │   ├── VelocityReport.js
│   │   │   └── CustomReportBuilder.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── README.md
├── ENHANCED_FEATURES.md             # Detailed feature documentation
├── RUN_INSTRUCTIONS.md              # How to run the application
├── AGILE_FEATURES.md                # Agile methodology features
└── TROUBLESHOOTING.md               # Common issues and solutions
```

## 🚀 Getting Started

### Prerequisites

- **Java 17** or higher
- **Node.js 16** or higher
- **Maven 3.6** or higher
- **npm** or yarn

### Quick Start

#### 1. Backend Setup

```bash
cd Agile/backend
mvn clean install
mvn spring-boot:run
```

Backend runs on: `http://localhost:8080`

#### 2. Frontend Setup

```bash
cd Agile/frontend
npm install
npm start
```

Frontend runs on: `http://localhost:3005`

### Access the Application

Open your browser and navigate to: **http://localhost:3005**

## 📊 Navigation Structure

- **Dashboard** - Overview of all projects and key metrics
- **Projects** - Create and manage projects, view team members
- **Team Management** - Add team members and assign to projects
- **Sprints & Tasks** - Create sprints, add tasks, assign work
- **Velocity Reports** - Track team velocity and trends
- **Health Reports** - Comprehensive project health dashboard (ALL metrics)
- **Custom Reports** - Build custom reports and export data

## 🔌 API Endpoints

### Projects
```
GET    /api/projects              - Get all projects
GET    /api/projects/{id}         - Get project by ID
POST   /api/projects              - Create new project
PUT    /api/projects/{id}         - Update project
DELETE /api/projects/{id}         - Delete project
```

### Project Members
```
GET    /api/projects/{projectId}/members           - Get project members
POST   /api/projects/{projectId}/members           - Add member to project
PUT    /api/projects/{projectId}/members/{id}      - Update member
DELETE /api/projects/{projectId}/members/{id}      - Remove member
POST   /api/projects/{projectId}/members/{id}/deactivate - Deactivate member
```

### Sprints
```
GET    /api/sprints                        - Get all sprints
GET    /api/sprints/{id}                   - Get sprint by ID
GET    /api/sprints/project/{projectId}    - Get sprints by project
POST   /api/sprints/project/{projectId}    - Create sprint
PUT    /api/sprints/{id}                   - Update sprint
DELETE /api/sprints/{id}                   - Delete sprint
```

### Tasks
```
GET    /api/tasks                    - Get all tasks
GET    /api/tasks/{id}               - Get task by ID
GET    /api/tasks/sprint/{sprintId}  - Get tasks by sprint
POST   /api/tasks/sprint/{sprintId}  - Create task
PUT    /api/tasks/{id}               - Update task
DELETE /api/tasks/{id}               - Delete task
```

### Defects
```
GET    /api/defects                  - Get all defects
GET    /api/defects/{id}             - Get defect by ID
GET    /api/defects/project/{id}     - Get defects by project
GET    /api/defects/sprint/{id}      - Get defects by sprint
GET    /api/defects/escaped          - Get escaped defects
POST   /api/defects                  - Create new defect
PUT    /api/defects/{id}             - Update defect
DELETE /api/defects/{id}             - Delete defect
```

### Reports
```
GET    /api/reports/velocity/{projectId}  - Get velocity report
GET    /api/reports/health/{projectId}    - Get health report
POST   /api/reports/pdf                   - Generate PDF report
```

## 📈 Enhanced Data Models

### Sprint (Enhanced)
```java
- sprintGoal (String)           // Sprint objective
- stakeholderFeedback (String)  // Sprint Review feedback
- goalAchieved (Boolean)        // Sprint success tracking
```

### Task (Enhanced)
```java
- type (TaskType enum)          // STORY, BUG, DEFECT, TASK, TECHNICAL_DEBT, SPIKE
```

### Defect (New Model)
```java
- severity (DefectSeverity)     // TRIVIAL, MINOR, MAJOR, CRITICAL, BLOCKER
- status (DefectStatus)         // NEW, OPEN, IN_PROGRESS, RESOLVED, CLOSED, REOPENED
- priority (DefectPriority)     // LOW, MEDIUM, HIGH, URGENT
- escaped (Boolean)             // Production bug flag
- rootCause (String)            // Root cause analysis
- foundBy, assignedTo           // Team member references
```

## 🎯 Supported Agile Metrics

### Project Health Tracking (10/10) ✅
1. ✅ Burndown Chart
2. ✅ Burn-up Chart
3. ✅ Cumulative Flow Diagram (CFD)
4. ✅ Definition of Done Adherence
5. ✅ Sprint Goal Achievement
6. ✅ Defect Trends / Quality Metrics
7. ✅ Stakeholder Feedback
8. ✅ Risk Indicators
9. ✅ Blocker Tracking
10. ✅ Technical Debt Tracking

### Team Velocity Tracking (3/3) ✅
1. ✅ Story Point Velocity
2. ✅ Average Velocity
3. ✅ Planned vs Actual

## 📖 Documentation

- **README.md** (this file) - Overview and getting started
- **ENHANCED_FEATURES.md** - Detailed feature documentation
- **RUN_INSTRUCTIONS.md** - Step-by-step running instructions
- **AGILE_FEATURES.md** - Agile methodology features
- **TASK_ASSIGNMENT_GUIDE.md** - Task assignment workflow
- **TROUBLESHOOTING.md** - Common issues and solutions

## 🔧 Configuration

### Backend Configuration
Edit `backend/src/main/resources/application.properties`:
```properties
server.port=8080
spring.h2.console.enabled=true
spring.jpa.hibernate.ddl-auto=update
```

### Frontend Configuration
Edit `frontend/src/services/api.js` to change API base URL:
```javascript
const API_BASE_URL = 'http://localhost:8080/api';
```

## 🎨 Usage Guide

### 1. Create a Project
- Go to **Projects** page
- Click "Create Project"
- Fill in project details (name, dates, status, health status, risk indicators)
- Submit

### 2. Add Team Members
- Go to **Team Management** page
- Click "Add Team Member"
- Select project, enter member details, choose Agile role
- Submit

### 3. Create Sprints
- Go to **Sprints & Tasks** page
- Select project
- Click "Create Sprint"
- Set sprint goal, dates, and planned story points
- Submit

### 4. Add Tasks
- In Sprint Management, select a sprint
- Click "Create Task"
- Choose task type, set priority, story points
- Assign to team member
- Submit

### 5. Track Progress
- Go to **Health Reports** to see all metrics
- View burndown, burn-up, CFD, defects, etc.
- Monitor sprint goal achievement
- Review stakeholder feedback

### 6. Generate Reports
- Go to **Custom Reports**
- Select project and configure report settings
- Generate visualization
- Export as JSON or Text

## 🧪 Testing

### Backend Tests
```bash
cd Agile/backend
mvn test
```

### Frontend Tests
```bash
cd Agile/frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 💡 Best Practices

### Sprint Management
- Always set clear, measurable sprint goals
- Record stakeholder feedback after every Sprint Review
- Mark goal achievement honestly for accurate metrics

### Task Classification
- Use **STORY** for user-facing features
- Use **BUG** for software defects found in testing
- Use **DEFECT** for production issues
- Use **TECHNICAL_DEBT** for code quality improvements
- Use **SPIKE** for research/investigation work

### Defect Management
- Log defects as soon as they're found
- Mark escaped defects to track quality
- Always record root cause for learning
- Update status regularly

### Health Monitoring
- Review health dashboard weekly
- Track trends, not just current state
- Address risks proactively
- Use feedback for continuous improvement

## 🆘 Support

For detailed troubleshooting, see **TROUBLESHOOTING.md**

For issues and questions, please create an issue in the repository.

## 🎉 Features Summary

This is a **production-ready** Agile project management system with:
- ✅ Complete project, sprint, and task management
- ✅ Team management with Agile roles
- ✅ All 10 standard Agile health metrics
- ✅ Comprehensive defect tracking
- ✅ Velocity tracking and forecasting
- ✅ Customizable reporting with export
- ✅ Real-time dashboards and visualizations
- ✅ Sprint goal and stakeholder feedback tracking
- ✅ Technical debt and blocker monitoring

**Ready to use for professional Agile project management!** 🚀
