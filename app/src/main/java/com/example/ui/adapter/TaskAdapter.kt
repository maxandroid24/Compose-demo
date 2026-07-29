package com.example.ui.adapter

import android.graphics.Color
import android.graphics.Paint
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.databinding.ItemTaskBinding
import com.example.domain.model.Priority
import com.example.domain.model.Task
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * RecyclerView Adapter for traditional XML layout task list (`item_task.xml`).
 * Uses ViewBinding [ItemTaskBinding] and [ListAdapter] for optimized updates.
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

            // Strikethrough for completed tasks
            if (task.isCompleted) {
                binding.tvTitle.paintFlags = binding.tvTitle.paintFlags or Paint.STRIKE_THRU_TEXT_FLAG
            } else {
                binding.tvTitle.paintFlags = binding.tvTitle.paintFlags and Paint.STRIKE_THRU_TEXT_FLAG.inv()
            }

            binding.cbCompleted.setOnCheckedChangeListener(null)
            binding.cbCompleted.isChecked = task.isCompleted
            binding.cbCompleted.setOnCheckedChangeListener { _, _ ->
                onToggleCompletion(task)
            }

            // Priority Chip
            binding.chipPriority.text = task.priority.name
            when (task.priority) {
                Priority.HIGH -> binding.chipPriority.setTextColor(Color.parseColor("#D32F2F"))
                Priority.URGENT -> binding.chipPriority.setTextColor(Color.parseColor("#B71C1C"))
                Priority.MEDIUM -> binding.chipPriority.setTextColor(Color.parseColor("#F57C00"))
                Priority.LOW -> binding.chipPriority.setTextColor(Color.parseColor("#388E3C"))
            }

            // Category Chip
            binding.chipCategory.text = task.category.name

            // Due Date
            if (task.dueDateMillis != null) {
                binding.tvDueDate.visibility = View.VISIBLE
                val formattedDate = SimpleDateFormat("MMM dd", Locale.getDefault()).format(Date(task.dueDateMillis))
                binding.tvDueDate.text = "Due: $formattedDate"
            } else {
                binding.tvDueDate.visibility = View.GONE
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
