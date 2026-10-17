import re
import html

def get_rule_based_explanation(line_num, raw_line, file_name, file_category):
    line = raw_line.strip()
    if not line:
        return None
    
    # Comments
    if line.startswith("//") or line.startswith("/*") or line.startswith("*") or line.startswith("*/"):
        return {
            "line": line_num,
            "code": line,
            "why": "Provides inline architectural documentation, parameter descriptions, or rationale for developers and IDE tooltips.",
            "what": "Ignored by the Kotlin compiler during bytecode generation; has zero runtime memory or execution overhead.",
            "concept": "Documentation & Code Readability"
        }
    
    # Package
    if line.startswith("package "):
        pkg = line.replace("package ", "").rstrip(";")
        return {
            "line": line_num,
            "code": line,
            "why": f"Defines the unique namespace `{pkg}` to organize the project according to Clean Architecture layers and prevent class naming collisions.",
            "what": "Tells the Kotlin compiler and JVM classloader the package path where this compiled class bytecode is placed in the output APK / DEX file.",
            "concept": "Namespace & Packaging Architecture"
        }
        
    # Import
    if line.startswith("import "):
        imp = line.replace("import ", "").rstrip(";")
        return {
            "line": line_num,
            "code": line,
            "why": f"Brings `{imp}` into local scope so that types, functions, or annotations can be referenced cleanly by simple name without verbose qualification.",
            "what": "Compile-time symbol resolution. The Kotlin compiler links symbol references during semantic analysis; imports create zero runtime overhead in bytecode.",
            "concept": "Dependency Resolution & Scope"
        }
        
    # Annotations
    if line.startswith("@AndroidEntryPoint"):
        return {
            "line": line_num,
            "code": line,
            "why": "Android Activities/Fragments are instantiated directly by the Android OS framework (via AppComponentFactory) rather than Dagger constructors. This annotation enables Hilt dependency injection.",
            "what": "Generates a Hilt subcomponent wrapper class (`Hilt_Activity`) that intercepts `onCreate()` to inject members and provide the injection context for `by viewModels()`.",
            "concept": "Dagger Hilt Framework Injection"
        }

    if line.startswith("@Composable"):
        return {
            "line": line_num,
            "code": line,
            "why": "Marks this Kotlin function as a declarative Jetpack Compose UI component capable of emitting nodes into the composition tree.",
            "what": "The Compose Compiler plugin intercepts this function to inject a `Composer` parameter, slot table management code, and recomposition scope registration.",
            "concept": "Jetpack Compose Runtime & Compiler"
        }

    if line.startswith("@HiltViewModel"):
        return {
            "line": line_num,
            "code": line,
            "why": "Identifies this ViewModel for automatic constructor injection by Hilt, eliminating manual `ViewModelProvider.Factory` boilerplate.",
            "what": "Generates a multibinding entry into Hilt's `ViewModelComponent`, allowing `by viewModels()` to instantiate it with all injected dependencies automatically.",
            "concept": "Hilt ViewModel Injection"
        }

    if line.startswith("@Entity"):
        return {
            "line": line_num,
            "code": line,
            "why": "Marks this data class as a persistent database table in the local SQLite database managed by Android Room ORM.",
            "what": "Room KSP processor generates SQL schema creation statements (`CREATE TABLE IF NOT EXISTS...`) and column mapping code.",
            "concept": "Room ORM Persistence"
        }

    if line.startswith("@Dao"):
        return {
            "line": line_num,
            "code": line,
            "why": "Defines a Data Access Object interface providing type-safe SQL query contracts for database interactions.",
            "what": "Room generates the concrete DAO implementation class (`TaskDao_Impl`) compiling raw SQL queries into SQLite cursor operations.",
            "concept": "Data Access Object (DAO) Pattern"
        }

    if line.startswith("@Database"):
        return {
            "line": line_num,
            "code": line,
            "why": "Declares the Room Database holder configuration, listing all entity tables, database version, and migration strategy.",
            "what": "Generates SQLite open helper implementations, schema hashes, and database instance caching via `Room.databaseBuilder()`.",
            "concept": "Room Database Configuration"
        }

    if line.startswith("@Module"):
        return {
            "line": line_num,
            "code": line,
            "why": "Informs Dagger Hilt that this Kotlin object contains dependency provision recipes (`@Provides` methods) for external classes (e.g. Room Database, Retrofit, OkHttpClient) that cannot use `@Inject constructor`.",
            "what": "Dagger compiler generates factory classes that Hilt incorporates into the dependency graph.",
            "concept": "Dagger Hilt Dependency Module"
        }

    if line.startswith("@InstallIn"):
        return {
            "line": line_num,
            "code": line,
            "why": "Specifies the Hilt component lifecycle scope (e.g., `SingletonComponent`, `ActivityComponent`) in which the module's dependencies live.",
            "what": "Binds the provided instances to the specified component scope, ensuring singletons persist across the entire application lifecycle.",
            "concept": "Hilt Component Scoping"
        }

    if line.startswith("@Inject constructor"):
        return {
            "line": line_num,
            "code": line,
            "why": "Instructs Dagger Hilt to use constructor injection, fulfilling all constructor arguments from the dependency graph automatically.",
            "what": "Dagger creates a `_Factory` class that retrieves dependencies from components and invokes the constructor.",
            "concept": "Constructor Dependency Injection"
        }

    if "enableEdgeToEdge()" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Adheres to Android 15 edge-to-edge system standards, removing default black letterboxes around status and navigation bars.",
            "what": "Configures `WindowCompat` and insets controllers so layout decor content spans the entire physical display, drawing under transparent system bars.",
            "concept": "Modern Android Insets & Edge-to-Edge"
        }

    if "super.onCreate(" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Mandatory lifecycle contract; notifies base framework classes (`AppCompatActivity` / `ComponentActivity`) to initialize state.",
            "what": "Restores saved instance state, registers saved state providers, and dispatches `Lifecycle.Event.ON_CREATE` to observers.",
            "concept": "Android Activity Lifecycle"
        }

    if "super.onDestroy()" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Mandatory lifecycle contract ensuring base class teardown logic completes safely.",
            "what": "Cleans up system resources and dispatches `Lifecycle.Event.ON_DESTROY`.",
            "concept": "Android Activity Teardown"
        }

    if "setContent {" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Replaces imperative XML `setContentView(R.layout.xxx)` with Jetpack Compose declarative UI composition.",
            "what": "Creates a `ComposeView`, sets it as the root content view of the Activity window, and initiates the initial UI composition.",
            "concept": "Compose UI Composition Root"
        }

    if "collectAsStateWithLifecycle()" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Safely observes `StateFlow` in Compose without leaking resources or wasting CPU/battery when the app is in the background.",
            "what": "Cancels flow subscription when lifecycle drops below `Lifecycle.State.STARTED`, resumes when resumed, and triggers recomposition on new emissions.",
            "concept": "Lifecycle-Aware Reactive Flow Collection"
        }

    if "repeatOnLifecycle(" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Recommended Android API to safely collect Coroutine flows in traditional XML Views without leaking jobs when the Activity is stopped.",
            "what": "Suspends the calling coroutine and spawns a child job that starts collecting when the lifecycle reaches the target state (e.g. `STARTED`) and cancels collection when the lifecycle falls below it.",
            "concept": "Lifecycle-Aware Coroutine Execution"
        }

    if "by viewModels()" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Kotlin property delegate scoping the ViewModel to this Activity's lifecycle, surviving configuration changes like screen rotations.",
            "what": "Queries the Activity's `ViewModelStore`. If an instance exists, returns it; otherwise requests Hilt's `HiltViewModelFactory` to instantiate it.",
            "concept": "ViewModel Lifecycle Retention & Property Delegation"
        }

    if "inflate(layoutInflater)" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Inflates XML layout into memory with compile-time type-safety, eliminating `findViewById` and null-pointer exceptions.",
            "what": "Parses XML layout file, instantiates view hierarchy, and binds direct references to the generated ViewBinding object.",
            "concept": "ViewBinding Pattern"
        }

    if "setContentView(binding.root)" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Attaches the inflated XML view hierarchy to the Activity's window.",
            "what": "Sets the root ViewGroup (`binding.root`) as the active visual display on screen.",
            "concept": "Window Content Attachment"
        }

    if "startActivity(Intent(" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Navigates the user to another Activity screen in the application.",
            "what": "Constructs an explicit `Intent` and dispatches it to Android's `ActivityManagerService` to push the new Activity onto the task backstack.",
            "concept": "Android Explicit Intent Navigation"
        }

    if "finish()" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Closes the current Activity and returns the user to the previous screen on the back stack.",
            "what": "Transitions the Activity through `onPause()`, `onStop()`, and `onDestroy()`, popping it from the task stack.",
            "concept": "Activity Stack Popping"
        }

    if "viewModelScope.launch" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Launches a Kotlin coroutine tied to the ViewModel's lifecycle, ensuring background jobs automatically cancel when the ViewModel is cleared.",
            "what": "Executes on `Dispatchers.Main.immediate` by default; automatically cancels all active child coroutines when `ViewModel.onCleared()` is invoked.",
            "concept": "Coroutine ViewModelScope Structured Concurrency"
        }

    if "withContext(Dispatchers.IO)" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Shifts execution off the Main/UI thread to background I/O worker threads to prevent UI freezes or ANR (Application Not Responding) dialogs.",
            "what": "Dispatches the block to Kotlin Coroutines thread pool optimized for disk reading, database queries, and network socket operations.",
            "concept": "Coroutine Dispatcher Thread Switching"
        }

    if "MutableStateFlow" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Holds mutable UI state that emits updates to observers whenever the value changes (hot stream with state replay).",
            "what": "Thread-safe reactive primitive holding the current value (`.value`); emits new values to all active collectors.",
            "concept": "Kotlin Coroutines StateFlow State Holder"
        }

    if "asStateFlow()" in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Exposes UI state as read-only `StateFlow` to the presentation layer, preventing external classes from modifying state directly.",
            "what": "Casts `MutableStateFlow` to read-only `StateFlow` interface, enforcing Unidirectional Data Flow (UDF).",
            "concept": "Encapsulation & Unidirectional Data Flow (UDF)"
        }

    # XML tags
    if line.startswith("<") and not line.startswith("<!--"):
        tag_match = re.search(r'<([a-zA-Z0-9_\.]+)', line)
        tag = tag_match.group(1) if tag_match else "XML Tag"
        return {
            "line": line_num,
            "code": line,
            "why": f"Declares UI layout component `{tag}` in the declarative XML view hierarchy.",
            "what": f"Instantiates the `{tag}` View / ViewGroup widget during layout inflation and registers its layout parameters.",
            "concept": "Android XML Layout Declaration"
        }

    if line.startswith("android:") or line.startswith("app:") or line.startswith("tools:"):
        return {
            "line": line_num,
            "code": line,
            "why": "Configures layout attributes (dimensions, constraints, padding, colors, or accessibility identifiers) for the parent XML view.",
            "what": "Parsed by Android `AttributeSet` during view construction to configure View layout params and styling properties.",
            "concept": "XML View Attributes & Constraints"
        }

    # Generic Kotlin declarations
    if line.startswith("class ") or " class " in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Defines a class blueprint encapsulating state, behavior, and lifecycle management for this architectural unit.",
            "what": "Allocates type metadata in the JVM classloader, establishes inheritance hierarchy, and defines member visibility.",
            "concept": "Object-Oriented Architecture"
        }

    if line.startswith("interface ") or " interface " in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Defines an abstraction contract separating the API definition from its concrete implementation, facilitating unit testing with mocks.",
            "what": "Declares abstract method signatures that implementing classes must satisfy.",
            "concept": "Dependency Inversion Principle (DIP)"
        }

    if line.startswith("data class "):
        return {
            "line": line_num,
            "code": line,
            "why": "Models immutable domain data or UI state. Kotlin automatically generates `equals()`, `hashCode()`, `toString()`, and `copy()` functions.",
            "what": "Allocates heap memory for immutable properties; `copy()` allows seamless state transformation in unidirectional data flow.",
            "concept": "Immutable Data Modeling"
        }

    if line.startswith("override fun ") or " override fun " in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Overrides a method defined in the parent class or interface to provide specialized implementation.",
            "what": "Virtual method table (vtable) dispatch routes invocations to this method override at runtime.",
            "concept": "Polymorphism & Contract Implementation"
        }

    if line.startswith("fun ") or " fun " in line:
        return {
            "line": line_num,
            "code": line,
            "why": "Encapsulates a reusable business logic, state mutation, or UI helper operation into a distinct callable function.",
            "what": "Allocates a stack frame on execution, runs contained statements, and returns the computed result.",
            "concept": "Functional Encapsulation"
        }

    if line.startswith("private val ") or line.startswith("val "):
        return {
            "line": line_num,
            "code": line,
            "why": "Declares an immutable property to hold dependencies, UI elements, or state values safely without side-effects.",
            "what": "Allocates instance field storage on the heap; prevents reassignment after initial value binding.",
            "concept": "Immutability & Encapsulation"
        }

    if line.startswith("private var ") or line.startswith("var "):
        return {
            "line": line_num,
            "code": line,
            "why": "Declares a mutable property whose value can be updated during runtime execution.",
            "what": "Allocates writable instance field storage on the heap with getter and setter methods.",
            "concept": "Mutable State Storage"
        }

    # Closing braces
    if line in ["}", "})", "},", "};", ")", "]", "];"]:
        return {
            "line": line_num,
            "code": line,
            "why": "Closes the block, lambda expression, parameter list, or class scope.",
            "what": "Demarcates stack frame scope, terminating local variable visibility.",
            "concept": "Syntax Scope Demarcation"
        }

    # Default fallback
    return {
        "line": line_num,
        "code": line,
        "why": f"Executes `{line[:45]}...` as part of this component's logic.",
        "what": "Evaluated sequentially by the Kotlin runtime / Android OS.",
        "concept": "Sequential Statement Execution"
    }

print("line_analyzer loaded successfully.")

