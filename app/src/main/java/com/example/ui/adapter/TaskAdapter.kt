package com.example.ui.adapter

import android.graphics.Paint
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.R
import com.example.databinding.ItemTaskBinding
import com.example.domain.model.Priority
import com.example.domain.model.Task
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * RecyclerView Adapter for traditional XML layout task list (`item_task.xml`).
 * Styled to match Jetpack Compose TaskCard.
 */
class TaskAdapter(
    private val onTaskClick: (Task) -> Unit,
    private val onToggleCompletion: (Task) -> Unit,
    private val onDeleteClick: (String) -> Unit
) : ListAdapter<Task, TaskAdapter.TaskViewHolder>(TaskDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TaskViewHolder {
        val binding = ItemTaskBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return TaskViewHolder(binding)
    }

    override fun onBindViewHolder(holder: TaskViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class TaskViewHolder(private val binding: ItemTaskBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(task: Task) {
            binding.tvTitle.text = task.title
            binding.tvDescription.text = task.description

            // Strikethrough and colors for completed tasks
            val context = binding.root.context
            val elevationPx = context.resources.displayMetrics.density * 2f

            if (task.isCompleted) {
                binding.tvTitle.paintFlags = binding.tvTitle.paintFlags or Paint.STRIKE_THRU_TEXT_FLAG
                binding.tvTitle.setTextColor(ContextCompat.getColor(context, R.color.on_surface_variant))
                binding.taskCard.setCardBackgroundColor(ContextCompat.getColor(context, R.color.surface_variant))
                binding.taskCard.cardElevation = 0f
            } else {
                binding.tvTitle.paintFlags = binding.tvTitle.paintFlags and Paint.STRIKE_THRU_TEXT_FLAG.inv()
                binding.tvTitle.setTextColor(ContextCompat.getColor(context, R.color.on_surface))
                binding.taskCard.setCardBackgroundColor(ContextCompat.getColor(context, R.color.surface))
                binding.taskCard.cardElevation = elevationPx
            }

            binding.cbCompleted.setOnCheckedChangeListener(null)
            binding.cbCompleted.isChecked = task.isCompleted
            binding.cbCompleted.setOnCheckedChangeListener { _, _ ->
                onToggleCompletion(task)
            }

            // Priority Bar
            val priorityColorRes = when (task.priority) {
                Priority.LOW -> R.color.priority_low
                Priority.MEDIUM -> R.color.priority_medium
                Priority.HIGH -> R.color.priority_high
                Priority.URGENT -> R.color.priority_urgent
            }
            binding.viewPriorityBar.setBackgroundColor(ContextCompat.getColor(context, priorityColorRes))

            // Category Chip
            binding.chipCategory.text = task.category.name

            // Due Date Chip
            if (task.dueDateMillis != null) {
                binding.chipDueDate.visibility = View.VISIBLE
                val formattedDate = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault()).format(Date(task.dueDateMillis))
                binding.chipDueDate.text = formattedDate
            } else {
                binding.chipDueDate.visibility = View.GONE
            }

            // Contact
            if (!task.assignedContactName.isNull_or_blank()) {
                binding.tvContact.visibility = View.VISIBLE
                binding.tvContact.text = "👤 ${task.assignedContactName}"
            } else {
                binding.tvContact.visibility = View.GONE
            }

            binding.btnDeleteTask.setOnClickListener {
                onDeleteClick(task.id)
            }

            binding.root.setOnClickListener {
                onTaskClick(task)
            }
        }
    }

    class TaskDiffCallback : DiffUtil.ItemCallback<Task>() {
        override fun areItemsTheSame(oldItem: Task, newItem: Task): Boolean = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Task, newItem: Task): Boolean = oldItem == newItem
    }
}

private fun String?.isNull_or_blank(): Boolean {
    return this == null || this.isBlank()
}
