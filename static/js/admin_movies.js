function confirmDelete(movieName) {
    return confirm(
        "Are you sure you want to delete \"" +
        movieName +
        "\"?\n\nThis action cannot be undone."
    );
}