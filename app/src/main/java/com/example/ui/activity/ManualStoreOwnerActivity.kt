package com.example.ui.activity

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.ViewModelStore
import androidx.lifecycle.ViewModelStoreOwner
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.example.TaskApplication
import com.example.databinding.ActivityManualStoreOwnerBinding
import com.example.domain.model.Category
import com.example.domain.model.Priority
import com.example.domain.model.Task
import com.example.ui.viewmodel.TaskViewModel
import kotlinx.coroutines.launch
import java.util.UUID

/**
 * Custom [ViewModelStoreOwner] implemented from scratch for a class or scope outside default activity delegates.
 *
 * Comparative Rationale:
 * - Standard Android: Uses `private val viewModel: TaskViewModel by viewModels()` property delegate on ComponentActivity.
 * - Custom Store Owner (This Pattern): Explicitly creates a [ViewModelStore], implements [ViewModelStoreOwner],
 *   instantiates [ViewModelProvider] with custom factory, and manages [ViewModelStore.clear] upon scope termination.
 */
class CustomViewModelStoreOwner : ViewModelStoreOwner {
    private val customStore = ViewModelStore()

    override val viewModelStore: ViewModelStore
        get() = customStore

    fun clearStore() {
        customStore.clear()
    }
}

class ManualStoreOwnerActivity : AppCompatActivity() {

    private lateinit var binding: ActivityManualStoreOwnerBinding

    // 1. Manually created ViewModelStoreOwner instance from scratch
    private val customStoreOwner = CustomViewModelStoreOwner()

    // 2. ViewModel instance retained inside our custom store owner
    private lateinit var viewModel: TaskViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityManualStoreOwnerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupToolbar()
        initializeManualViewModel()
        setupListeners()
        observeManualViewModel()
    }

    private fun setupToolbar() {
        binding.toolbar.setNavigationOnClickListener { finish() }
    }

    /**
     * Demonstrates creating a ViewModel manually from scratch using [ViewModelProvider]
     * and a custom [ViewModelStoreOwner] instance instead of `by viewModels()`.
     */
    private fun initializeManualViewModel() {
        val appContainer = (application as TaskApplication).appContainer
        val factory = appContainer.provideTaskViewModelFactory()

        // Explicitly obtain TaskViewModel from our custom store owner using ViewModelProvider
        viewModel = ViewModelProvider(
            owner = customStoreOwner,
            factory = factory
        )[TaskViewModel::class.java]

        updateCreationInfoText()
    }

    private fun updateCreationInfoText() {
        binding.tvCreationInfo.text = """
            Owner: CustomViewModelStoreOwner
            Store Hashcode: ${customStoreOwner.viewModelStore.hashCode()}
            ViewModel Instance: TaskViewModel@${Integer.toHexString(viewModel.hashCode())}
            Creation Method: ViewModelProvider(customStoreOwner, factory)[TaskViewModel::class.java]
        """.trimIndent()
    }

    private fun setupListeners() {
        // Recreate ViewModel by clearing custom store manually
        binding.btnRecreateViewModel.setOnClickListener {
            customStoreOwner.clearStore()
            initializeManualViewModel()
            observeManualViewModel()
            Toast.makeText(this, "Cleared ViewModelStore & Recreated ViewModel!", Toast.LENGTH_SHORT).show()
        }

        // Add a new task using the manually created ViewModel
        binding.btnAddNewTaskManual.setOnClickListener {
            val task = Task(
                id = UUID.randomUUID().toString(),
                title = "Manual Store Task #${(100..999).random()}",
                description = "Created via ViewModel instantiated from custom ViewModelStoreOwner",
                isCompleted = false,
                priority = Priority.HIGH,
                category = Category.WORK,
                dueDateMillis = System.currentTimeMillis() + 86400000L
            )
            viewModel.prepareEditTask(task)
            viewModel.saveTask()
            Toast.makeText(this, "Saved task via manual ViewModel!", Toast.LENGTH_SHORT).show()
        }
    }

    private fun observeManualViewModel() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.listUiState.collect { state ->
                    binding.tvLiveTaskCount.text = "Loaded ${state.tasks.size} task(s) from manual ViewModel state."
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // 3. Crucial: Clean up custom ViewModelStore when this Activity / Scope is destroyed
        customStoreOwner.clearStore()
    }
}
