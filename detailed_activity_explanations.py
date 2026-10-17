# Detailed, expert line-by-line explanations for all 10 Activities

ACTIVITY_LINE_EXPLANATIONS = {
    "act_main": [
        {
            "line": 1,
            "code": "package com.example",
            "why": "Defines the base application package namespace, organizing all entry-point and application-level classes in clean architecture.",
            "what": "Directs the Kotlin compiler and JVM classloader to package this class in the root `com.example` namespace.",
            "concept": "Kotlin Package Namespace"
        },
        {
            "lines": [3, 17],
            "code": "import android.content.Intent\nimport android.os.Bundle\nimport androidx.activity.enableEdgeToEdge\nimport androidx.appcompat.app.AppCompatActivity\n...",
            "why": "Brings Android framework classes (`Intent`, `Bundle`), Jetpack insets (`enableEdgeToEdge`), ViewBinding (`ActivityMainBinding`), Dagger Hilt (`AndroidEntryPoint`), and all 10 Activity classes into scope.",
            "what": "Resolves class symbols at compile time so simple names can be used without runtime performance cost.",
            "concept": "Symbol Resolution & Clean Scope"
        },
        {
            "line": 26,
            "code": "@AndroidEntryPoint",
            "why": "Standard Android Activities are instantiated directly by the Android OS framework (via AppComponentFactory) rather than Dagger constructors. This annotation enables Hilt dependency injection.",
            "what": "Generates an internal Hilt wrapper class (`Hilt_MainActivity`) that hooks into `onCreate()` to inject dependencies and provides the injection scope for ViewModels.",
            "concept": "Dagger Hilt Framework Injection"
        },
        {
            "line": 27,
            "code": "class MainActivity : AppCompatActivity()",
            "why": "Serves as the primary entry point / launcher Activity defined in AndroidManifest.xml. Extends AppCompatActivity to support ViewBinding, backward-compatible ActionBar, and Fragment transactions.",
            "what": "Allocates the Activity instance in Android's ActivityManagerService (AMS), creating the window decor and managing backstack navigation.",
            "concept": "Activity Lifecycle & AppCompat"
        },
        {
            "line": 29,
            "code": "private lateinit var binding: ActivityMainBinding",
            "why": "Uses ViewBinding to eliminate unsafe `findViewById` calls and guarantee compile-time type-safety and null-safety for all XML layout views.",
            "what": "Allocates an uninitialized reference on the Activity heap. It is initialized in `onCreate()` when inflating `activity_main.xml`.",
            "concept": "ViewBinding Pattern"
        },
        {
            "line": 31,
            "code": "override fun onCreate(savedInstanceState: Bundle?)",
            "why": "The fundamental lifecycle callback invoked when the system first instantiates the Activity.",
            "what": "Entry point where layout inflation, dependency resolution, button listeners, and background sync scheduling take place.",
            "concept": "Activity Creation Lifecycle"
        },
        {
            "line": 32,
            "code": "super.onCreate(savedInstanceState)",
            "why": "Mandatory contract in Android lifecycle methods to let base classes restore saved instance states and initialize the LifecycleRegistry.",
            "what": "Executes `AppCompatActivity.onCreate()`, transitioning lifecycle state to `Lifecycle.State.CREATED`.",
            "concept": "Lifecycle Protocol & State Restoration"
        },
        {
            "line": 33,
            "code": "enableEdgeToEdge()",
            "why": "Adheres to modern Android 15 edge-to-edge guidelines, drawing UI beneath transparent system bars rather than ugly letterboxes.",
            "what": "Configures `WindowCompat` and insets controllers so layout decor content spans the entire physical display, drawing under transparent status and navigation bars.",
            "concept": "Modern Android Insets & Edge-to-Edge"
        },
        {
            "line": 35,
            "code": "binding = ActivityMainBinding.inflate(layoutInflater)",
            "why": "Inflates the XML layout `res/layout/activity_main.xml` into memory with compile-time type-safety.",
            "what": "Traverses the XML hierarchy, instantiates View objects, and binds them to direct fields on the generated `ActivityMainBinding` instance.",
            "concept": "XML View Hierarchy Inflation"
        },
        {
            "line": 36,
            "code": "setContentView(binding.root)",
            "why": "Attaches the inflated XML view hierarchy to the Activity's window decor view.",
            "what": "Makes the root ConstraintLayout (`binding.root`) the active visible display for the user on screen.",
            "concept": "Window Content Attachment"
        },
        {
            "lines": [38, 41],
            "code": "val appContainer = (application as TaskApplication).appContainer\nappContainer.workManagerScheduler.schedulePeriodicSync()",
            "why": "Starts background 15-minute periodic task synchronization as soon as the app is launched.",
            "what": "Casts `Application` to `TaskApplication`, accesses the manual dependency injection `appContainer`, and enqueues a `PeriodicWorkRequest` into Android's WorkManager SQLite queue with network connectivity constraints.",
            "concept": "Persistent Background WorkManager Scheduling"
        },
        {
            "line": 42,
            "code": "setupButtons()",
            "why": "Organizes UI setup cleanly into dedicated private helper methods rather than cluttering `onCreate()`.",
            "what": "Invokes button click listener attachments.",
            "concept": "Code Modularization"
        },
        {
            "lines": [45, 53],
            "code": "binding.btnOpenTaskListCompose.setOnClickListener { ... }\nbinding.btnOpenTaskListXml.setOnClickListener { ... }",
            "why": "Allows users to immediately compare the Task List screen implemented in pure Jetpack Compose vs. traditional XML + RecyclerView.",
            "what": "Constructs explicit `Intent(this, TaskListComposeActivity::class.java)` or `Intent(this, TaskListXmlActivity::class.java)` and dispatches to `startActivity()`.",
            "concept": "Explicit Intent Paradigm Routing"
        },
        {
            "lines": [54, 61],
            "code": "binding.btnOpenTaskDetailCompose.setOnClickListener { ... }\nbinding.btnOpenTaskDetailXml.setOnClickListener { ... }",
            "why": "Enables comparison of complex form inputs, bidirectional text input, chip selectors, and validation between Compose and XML.",
            "what": "Launches either `TaskDetailComposeActivity` or `TaskDetailXmlActivity`.",
            "concept": "Form Paradigm Navigation"
        },
        {
            "lines": [62, 69],
            "code": "binding.btnOpenAnalyticsCompose.setOnClickListener { ... }\nbinding.btnOpenAnalyticsXml.setOnClickListener { ... }",
            "why": "Compares data visualization (canvas graphs, animated progress bars, metric cards) in Compose vs XML Views.",
            "what": "Launches either `TaskAnalyticsComposeActivity` or `TaskAnalyticsXmlActivity`.",
            "concept": "Data Visualization Routing"
        },
        {
            "lines": [70, 77],
            "code": "binding.btnOpenSettingsCompose.setOnClickListener { ... }\nbinding.btnOpenSettingsXml.setOnClickListener { ... }",
            "why": "Compares settings toggles and manual sync triggers between Compose and XML.",
            "what": "Launches either `SettingsComposeActivity` or `SettingsXmlActivity`.",
            "concept": "Settings Paradigm Routing"
        },
        {
            "lines": [78, 87],
            "code": "binding.btnOpenStandardViewModel.setOnClickListener { ... }\nbinding.btnOpenManualViewModel.setOnClickListener { ... }",
            "why": "Demonstrates standard Android `by viewModels()` property delegation versus creating a custom `ViewModelStoreOwner` from scratch.",
            "what": "Launches `TaskListComposeActivity` (standard) or `ManualStoreOwnerActivity` (custom lifecycle store owner).",
            "concept": "ViewModel Architecture Evaluation"
        }
    ],

    "act_task_list_compose": [
        {
            "line": 42,
            "code": "@AndroidEntryPoint",
            "why": "Enables Hilt dependency injection in this Compose Activity.",
            "what": "Hooks into Activity lifecycle to provide Hilt dependency resolution.",
            "concept": "Dagger Hilt Injection"
        },
        {
            "line": 43,
            "code": "class TaskListComposeActivity : ComponentActivity()",
            "why": "Jetpack Compose activities don't need the legacy XML overhead of AppCompatActivity. ComponentActivity provides the bare-minimum foundation (LifecycleOwner, ViewModelStoreOwner, SavedStateRegistryOwner).",
            "what": "Minimizes framework overhead, reducing activity creation latency.",
            "concept": "Lightweight ComponentActivity Host"
        },
        {
            "line": 45,
            "code": "private val viewModel: TaskViewModel by viewModels()",
            "why": "Retains a TaskViewModel instance scoped to this Activity that survives screen rotation, theme changes, and window resizing.",
            "what": "Uses Kotlin property delegation (`by viewModels()`). On initial call, creates the ViewModel using Hilt's ViewModel factory; on subsequent calls across configuration changes, retrieves the cached instance from `viewModelStore`.",
            "concept": "Retained ViewModel Scoping"
        },
        {
            "line": 49,
            "code": "enableEdgeToEdge()",
            "why": "Implements modern edge-to-edge drawing under system bars.",
            "what": "Adjusts window insets to allow the UI to flow behind status and navigation bars.",
            "concept": "Edge-to-Edge Display"
        },
        {
            "line": 51,
            "code": "setContent {",
            "why": "Jetpack Compose entry point that replaces XML `setContentView(R.layout.xxx)`.",
            "what": "Creates a `ComposeView`, sets it as the Activity's root content view, and launches the Compose composition tree.",
            "concept": "Compose UI Composition Root"
        },
        {
            "line": 52,
            "code": "TaskManagerTheme {",
            "why": "Injects Material 3 design tokens (colors, typography, shapes) via Compose `CompositionLocal`.",
            "what": "Applies `MaterialTheme` colors, ensuring components adapt to system light/dark mode.",
            "concept": "Material 3 Theming Hierarchy"
        },
        {
            "line": 53,
            "code": "val listUiState by viewModel.listUiState.collectAsStateWithLifecycle()",
            "why": "Safely collects `StateFlow<TaskListUiState>` from the ViewModel in a lifecycle-aware manner.",
            "what": "Uses `collectAsStateWithLifecycle()` to automatically pause flow collection when the Activity enters the background (lifecycle < `STARTED`), preventing battery drain and background UI calculations. When resumed, resumes collection and triggers recomposition on new state emissions.",
            "concept": "Lifecycle-Aware Flow Collection"
        },
        {
            "lines": [55, 87],
            "code": "Scaffold(topBar = { ... })",
            "why": "Provides standard Material Design slot structure for top bar, bottom bar, and content.",
            "what": "Measures system and top bar heights, calculates `innerPadding`, and passes it to the body content lambda to prevent overlap.",
            "concept": "Material 3 Scaffold Layout"
        },
        {
            "lines": [58, 86],
            "code": "Column(modifier = Modifier.fillMaxWidth().background(Color(0xFFE8F0FE)).statusBarsPadding()) { ... }",
            "why": "Provides an instant 'Switch to XML 📄' button to switch paradigms seamlessly.",
            "what": "Renders a `Column` with `statusBarsPadding()` and a `Row` containing a `TextButton` that launches `TaskListXmlActivity` and finishes the current activity.",
            "concept": "Comparison Header Banner"
        },
        {
            "lines": [88, 114],
            "code": "innerPadding -> Box(modifier = Modifier.padding(innerPadding)) { TaskListScreen(...) }",
            "why": "Applies Scaffold insets padding and invokes the stateless TaskListScreen composable.",
            "what": "Emits `TaskListScreen` into the composition slot table, passing `listUiState` downward and passing event lambdas (`onSearchQueryChanged`, `onToggleTaskCompletion`, etc.) upward to the ViewModel.",
            "concept": "Unidirectional Data Flow (UDF)"
        },
        {
            "lines": [98, 101],
            "code": "onTaskClick = { task -> viewModel.prepareEditTask(task); startActivity(Intent(..., TaskDetailComposeActivity::class.java)) }",
            "why": "Handles navigation when a task card is clicked.",
            "what": "Prepares the task in `TaskViewModel` for editing and launches `TaskDetailComposeActivity`.",
            "concept": "Stateful Intent Navigation"
        }
    ],

    "act_task_list_xml": [
        {
            "line": 31,
            "code": "class TaskListXmlActivity : AppCompatActivity()",
            "why": "Extends `AppCompatActivity` to support XML ViewBinding, Toolbar support, and Material Components.",
            "what": "Creates the traditional Android view hierarchy host.",
            "concept": "XML Activity Host"
        },
        {
            "line": 33,
            "code": "private lateinit var binding: ActivityTaskListBinding",
            "why": "Eliminates `findViewById` boilerplate; provides compile-time type-safety for `activity_task_list.xml`.",
            "what": "Stores reference to the generated ViewBinding object.",
            "concept": "Type-Safe ViewBinding"
        },
        {
            "line": 35,
            "code": "private lateinit var taskAdapter: TaskAdapter",
            "why": "Traditional XML requires an explicit `RecyclerView.Adapter` to bind domain data to XML view items.",
            "what": "Manages `TaskViewHolder` instantiation and binds `Task` items to `item_task.xml`.",
            "concept": "RecyclerView Adapter Pattern"
        },
        {
            "lines": [37, 47],
            "code": "override fun onCreate(savedInstanceState: Bundle?) { ... }",
            "why": "Initializes the imperative view hierarchy.",
            "what": "Inflates `activity_task_list.xml`, attaches to window decor view, sets up toolbar, configures RecyclerView, registers input listeners, and starts ViewModel flow observation.",
            "concept": "Imperative Activity Initialization"
        },
        {
            "lines": [49, 61],
            "code": "private fun setupToolbar() { ... }",
            "why": "Configures navigation icons and the 'Switch to Compose ⚡' button.",
            "what": "Sets click listeners on `binding.toolbar` and navigation buttons.",
            "concept": "Toolbar Configuration"
        },
        {
            "lines": [63, 80],
            "code": "private fun setupRecyclerView() { ... }",
            "why": "Imperative list management; sets up the `LinearLayoutManager` and passes lambda callbacks for item clicks, completion toggling, and deletion.",
            "what": "Attaches the adapter to `binding.recyclerViewTasks` and configures vertical item scrolling.",
            "concept": "RecyclerView Configuration"
        },
        {
            "lines": [88, 94],
            "code": "binding.etSearchQuery.addTextChangedListener(...) ",
            "why": "Listens to text changes in the search input box imperatively.",
            "what": "Implements `TextWatcher` and calls `viewModel.onSearchQueryChanged(s?.toString().orEmpty())` on every keystroke.",
            "concept": "Imperative TextWatcher"
        },
        {
            "lines": [96, 107],
            "code": "binding.chipGroupCategory.setOnCheckedStateChangeListener(...) ",
            "why": "Listens to category chip filter selections.",
            "what": "Evaluates checked chip IDs and updates the category filter in `TaskViewModel`.",
            "concept": "ChipGroup State Observation"
        },
        {
            "lines": [117, 133],
            "code": "lifecycleScope.launch { repeatOnLifecycle(Lifecycle.State.STARTED) { viewModel.listUiState.collect { ... } } }",
            "why": "Safely observes `StateFlow` in XML Views without background resource leakage.",
            "what": "`repeatOnLifecycle(Lifecycle.State.STARTED)` pauses the coroutine when the activity stops, preventing background memory leaks. Inside the collector, manually updates the UI: submits items to `taskAdapter.submitList()` (running DiffUtil in the background), toggles `progressBar.visibility`, and updates empty state text.",
            "concept": "repeatOnLifecycle Flow Collection"
        }
    ],

    "act_task_detail_compose": [
        {
            "line": 40,
            "code": "class TaskDetailComposeActivity : ComponentActivity()",
            "why": "Lightweight Jetpack Compose host for the Task Detail & Edit screen.",
            "what": "Serves as the lifecycle and window container without XML layout inflation.",
            "concept": "Lightweight Compose Activity Host"
        },
        {
            "line": 42,
            "code": "private val viewModel: TaskViewModel by viewModels()",
            "why": "Obtains the scoped `TaskViewModel` containing `detailUiState`.",
            "what": "Provides shared state between list and detail screens when navigated within the same process.",
            "concept": "Retained ViewModel State"
        },
        {
            "line": 46,
            "code": "enableEdgeToEdge()",
            "why": "Enforces edge-to-edge drawing under system bars.",
            "what": "Sets system bar colors to transparent and expands layout bounds to physical screen edges.",
            "concept": "Edge-to-Edge Modern Design"
        },
        {
            "line": 50,
            "code": "val detailUiState by viewModel.detailUiState.collectAsStateWithLifecycle()",
            "why": "Subscribes to detail state (task title, description, priority, category, due date, contact).",
            "what": "Automatically recomposes form fields as the user types or updates selections.",
            "concept": "Declarative Form State Binding"
        },
        {
            "lines": [86, 96],
            "code": "TaskDetailScreen(uiState = detailUiState, onTitleChanged = viewModel::onDetailTitleChanged, ...)",
            "why": "Invokes the composable form screen, passing UI state and event handlers.",
            "what": "Binds form inputs to `viewModel::onDetailTitleChanged`, `viewModel::onDetailDescriptionChanged`, `viewModel::saveTask`, etc.",
            "concept": "Unidirectional Data Flow Form"
        },
        {
            "line": 95,
            "code": "onBackClick = { finish() }",
            "why": "Handles the back navigation action when user taps back icon.",
            "what": "Finishes the activity, popping it from the task stack and returning to the list screen.",
            "concept": "Activity Navigation Stack"
        }
    ],

    "act_task_detail_xml": [
        {
            "line": 33,
            "code": "class TaskDetailXmlActivity : AppCompatActivity()",
            "why": "Traditional XML form Activity hosting `activity_task_detail.xml`.",
            "what": "Handles complex imperative form binding with multiple `TextWatcher` instances and `ChipGroup` listeners.",
            "concept": "XML Form Activity Host"
        },
        {
            "lines": [57, 71],
            "code": "binding.etTitle.addTextChangedListener(...) \nbinding.etDescription.addTextChangedListener(...) ",
            "why": "Captures keystrokes in `TextInputEditText` fields.",
            "what": "Calls `viewModel.onDetailTitleChanged()` and `viewModel.onDetailDescriptionChanged()` on text change.",
            "concept": "Imperative TextWatcher Synchronization"
        },
        {
            "lines": [73, 91],
            "code": "binding.chipGroupPriority.setOnCheckedStateChangeListener { ... }\nbinding.chipGroupCategoryDetail.setOnCheckedStateChangeListener { ... }",
            "why": "Captures single-select chip clicks.",
            "what": "Maps XML chip IDs to Domain enum values (`Priority.LOW`, `Priority.HIGH`, `Category.WORK`, etc.).",
            "concept": "ChipGroup Option Mapping"
        },
        {
            "lines": [93, 100],
            "code": "binding.cardDueDate.setOnClickListener { ... }",
            "why": "Allows toggling a 24-hour reminder timestamp.",
            "what": "Sets or clears `dueDateMillis` in `TaskViewModel`.",
            "concept": "Date Selection Event"
        },
        {
            "lines": [102, 104],
            "code": "binding.cardAssignContact.setOnClickListener { showContactPickerDialog() }",
            "why": "Opens contact picker dialog querying Android contacts.",
            "what": "Triggers `showContactPickerDialog()` using `ContactsProviderManager`.",
            "concept": "ContentProvider Integration"
        },
        {
            "lines": [111, 152],
            "code": "private fun observeViewModel() { ... }",
            "why": "Updates XML views in response to ViewModel flow emissions.",
            "what": "Observes `detailUiState`. Checks `if (binding.etTitle.text.toString() != state.title)` before calling `setText(state.title)` to avoid infinite cursor resetting loops! Handles `state.saveSuccess` by displaying a `Toast` and calling `finish()`.",
            "concept": "Cursor Preservation & State Reflection"
        },
        {
            "lines": [154, 167],
            "code": "private fun showContactPickerDialog() { ... }",
            "why": "Demonstrates Android inter-process communication using `ContentResolver` to query contacts.",
            "what": "`ContactsProviderManager` queries contacts, and `AlertDialog.Builder` displays a selection list.",
            "concept": "Inter-Process ContentResolver Query"
        }
    ],

    "act_analytics_compose": [
        {
            "line": 40,
            "code": "class TaskAnalyticsComposeActivity : ComponentActivity()",
            "why": "Lightweight Compose host for the analytics and productivity dashboard.",
            "what": "Hosts Compose canvas graphs, completion rate indicators, and metric cards.",
            "concept": "Compose Analytics Host"
        },
        {
            "line": 50,
            "code": "val analyticsUiState by viewModel.analyticsUiState.collectAsStateWithLifecycle()",
            "why": "Collects real-time aggregated metrics computed by `GetTaskAnalyticsUseCase`.",
            "what": "Re-renders the analytics screen whenever tasks are completed, added, or deleted.",
            "concept": "Reactive Metrics Flow"
        },
        {
            "lines": [86, 89],
            "code": "TaskAnalyticsScreen(uiState = analyticsUiState, onBackClick = { finish() })",
            "why": "Renders declarative charts, circular progress indicators, and priority distribution bars.",
            "what": "Emits analytics UI into the composition tree.",
            "concept": "Declarative Data Visualization"
        }
    ],

    "act_analytics_xml": [
        {
            "line": 27,
            "code": "class TaskAnalyticsXmlActivity : AppCompatActivity()",
            "why": "Traditional XML host for the analytics dashboard using `activity_task_analytics.xml`.",
            "what": "Manages `TaskAnalyticsFragment` or directly manipulates XML `ProgressBar` widgets and TextViews.",
            "concept": "XML Analytics Host"
        },
        {
            "lines": [40, 75],
            "code": "binding.progressCompletion.progress = ...\nbinding.tvTotalTasksCount.text = ...",
            "why": "In XML, progress bars and text metrics must be updated manually via code.",
            "what": "Calculates percentages, updates `binding.progressCompletion.progress`, formats metric text strings, and animates `ObjectAnimator.ofInt(...)`.",
            "concept": "Imperative Progress Animation"
        }
    ],

    "act_settings_compose": [
        {
            "line": 40,
            "code": "class SettingsComposeActivity : ComponentActivity()",
            "why": "Compose host for application preferences and manual background sync trigger.",
            "what": "Hosts `SettingsScreen` composable with declarative switches and sync progress cards.",
            "concept": "Compose Settings Host"
        },
        {
            "line": 50,
            "code": "val syncUiState by viewModel.syncUiState.collectAsStateWithLifecycle()",
            "why": "Collects WorkManager sync status (`SyncUiState.Idle`, `SyncUiState.Syncing`, `SyncUiState.Success`, `SyncUiState.Error`).",
            "what": "Updates Compose sync status card reactively as WorkManager completes sync operations.",
            "concept": "WorkManager State Observation"
        },
        {
            "lines": [86, 90],
            "code": "SettingsScreen(syncUiState = syncUiState, onTriggerSyncClick = viewModel::triggerManualSync, ...)",
            "why": "Connects user actions (`onTriggerSyncClick = viewModel::triggerManualSync`) to the ViewModel.",
            "what": "Triggers immediate one-time WorkManager task synchronization.",
            "concept": "Manual Background Sync Trigger"
        }
    ],

    "act_settings_xml": [
        {
            "line": 27,
            "code": "class SettingsXmlActivity : AppCompatActivity()",
            "why": "Traditional XML host for settings and synchronization controls.",
            "what": "Inflates `activity_settings.xml`, binds `SwitchMaterial` widgets, and handles button clicks.",
            "concept": "XML Settings Host"
        },
        {
            "lines": [55, 80],
            "code": "viewModel.syncUiState.collect { state -> binding.btnTriggerSync.isEnabled = state !is SyncUiState.Syncing ... }",
            "why": "Manually observes `syncUiState` and toggles XML `ProgressBar`, `TextView`, and `Button.isEnabled`.",
            "what": "Sets button to disabled during sync, updates status text, and displays a `Toast` on sync completion.",
            "concept": "Imperative Sync State Binding"
        }
    ],

    "act_manual_store_owner": [
        {
            "lines": [29, 38],
            "code": "class CustomViewModelStoreOwner : ViewModelStoreOwner {\n    private val customStore = ViewModelStore()\n    override val viewModelStore: ViewModelStore get() = customStore\n    fun clearStore() { customStore.clear() }\n}",
            "why": "Crucial architectural demonstration: creates a custom `ViewModelStoreOwner` from scratch rather than relying on Android framework default `by viewModels()`.",
            "what": "Implements `ViewModelStoreOwner`, instantiates an explicit `ViewModelStore()`, and exposes `clearStore()` to manually wipe retained ViewModels from memory.",
            "concept": "Custom ViewModelStoreOwner Pattern"
        },
        {
            "line": 40,
            "code": "class ManualStoreOwnerActivity : AppCompatActivity()",
            "why": "Demonstrates low-level Android ViewModel lifecycle mechanics, manual `ViewModelProvider` construction, and custom store scoping.",
            "what": "Holds a dedicated `customStoreOwner` instance and manually manages its lifecycle.",
            "concept": "Manual Lifecycle Scoping"
        },
        {
            "lines": [69, 80],
            "code": "val appContainer = (application as TaskApplication).appContainer\nval factory = appContainer.provideTaskViewModelFactory()\nviewModel = ViewModelProvider(owner = customStoreOwner, factory = factory)[TaskViewModel::class.java]",
            "why": "Demonstrates how `ViewModelProvider` works under the hood when `by viewModels()` is called.",
            "what": "Obtains the custom ViewModelFactory from manual DI container, instantiates `ViewModelProvider` targeting our `customStoreOwner`, and retrieves or creates `TaskViewModel`.",
            "concept": "Under-the-Hood ViewModelProvider Instantiation"
        },
        {
            "lines": [82, 89],
            "code": "updateCreationInfoText()",
            "why": "Visual proof in the UI of the custom store hashcode, ViewModel instance hex address, and creation method.",
            "what": "Prints live runtime reflection data to `binding.tvCreationInfo`.",
            "concept": "Runtime Reflection Inspection"
        },
        {
            "lines": [93, 98],
            "code": "binding.btnRecreateViewModel.setOnClickListener {\n    customStoreOwner.clearStore()\n    initializeManualViewModel()\n    observeManualViewModel()\n    Toast.makeText(this, \"Cleared ViewModelStore & Recreated ViewModel!\", Toast.LENGTH_SHORT).show()\n}",
            "why": "Demonstrates manual memory clearance: calls `customStoreOwner.clearStore()` to invoke `ViewModel.onCleared()`, then re-creates the ViewModel.",
            "what": "Wipes the store, clears state, instantiates a fresh ViewModel, and shows a Toast.",
            "concept": "Manual Store Invalidation"
        },
        {
            "lines": [125, 132],
            "code": "override fun onDestroy() {\n    super.onDestroy()\n    if (isFinishing) {\n        customStoreOwner.clearStore()\n    }\n}",
            "why": "Critical memory leak prevention! Because `customStoreOwner` is not managed by Android framework `ComponentActivity`, we must manually invoke `clearStore()` when the Activity is finishing (`isFinishing == true`).",
            "what": "Calls `ViewModelStore.clear()`, which iterates over all stored ViewModels, calls `ViewModel.onCleared()` to cancel coroutine scopes, and frees heap memory.",
            "concept": "Explicit Memory Teardown Contract"
        }
    ]
}

print("Activity explanations loaded successfully.")

