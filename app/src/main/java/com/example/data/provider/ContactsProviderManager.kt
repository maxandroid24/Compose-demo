package com.example.data.provider

import android.content.Context
import android.provider.ContactsContract
import android.util.Log

/**
 * Domain model representing a contact fetched from Android ContentProvider.
 */
data class ContactInfo(
    val id: String,
    val name: String,
    val phoneNumber: String
)

/**
 * Manager querying device contacts using Android's ContentProvider architecture (`ContactsContract`).
 *
 * Architectural Pattern & Decision Rationale:
 * - ContentProvider is Android's standard interface for accessing shared cross-app data sources.
 * - Why preferred: Interoperates natively with system Contacts, allowing tasks to be assigned to
 *   real contacts/team members.
 */
class ContactsProviderManager(private val context: Context) {

    /**
     * Reads contacts from `ContactsContract.CommonDataKinds.Phone.CONTENT_URI` using ContentResolver.
     */
    fun fetchContacts(): List<ContactInfo> {
        val contacts = mutableListOf<ContactInfo>()
        val contentResolver = context.contentResolver

        val projection = arrayOf(
            ContactsContract.CommonDataKinds.Phone.CONTACT_ID,
            ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
            ContactsContract.CommonDataKinds.Phone.NUMBER
        )

        try {
            val cursor = contentResolver.query(
                ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                projection,
                null,
                null,
                "${ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME} ASC"
            )

            cursor?.use {
                val idIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.CONTACT_ID)
                val nameIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
                val numberIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)

                while (it.moveToNext()) {
                    val id = if (idIndex >= 0) it.getString(idIndex) else ""
                    val name = if (nameIndex >= 0) it.getString(nameIndex) ?: "Unknown" else "Unknown"
                    val number = if (numberIndex >= 0) it.getString(numberIndex) ?: "" else ""

                    if (name.isNotBlank() && contacts.none { c -> c.name == name && c.phoneNumber == number }) {
                        contacts.add(ContactInfo(id = id, name = name, phoneNumber = number))
                    }
                }
            }
        } catch (e: Exception) {
            Log.e("ContactsProvider", "Error querying ContactsContract ContentProvider: ${e.message}")
        }

        // If system contacts are empty (e.g. emulator without contacts), provide sample fallback options
        if (contacts.isEmpty()) {
            contacts.addAll(
                listOf(
                    ContactInfo("1", "Alex Johnson", "+1 555-0192"),
                    ContactInfo("2", "Sarah Smith", "+1 555-0148"),
                    ContactInfo("3", "David Chen", "+1 555-0177"),
                    ContactInfo("4", "Maria Garcia", "+1 555-0133")
                )
            )
        }

        return contacts
    }
}
